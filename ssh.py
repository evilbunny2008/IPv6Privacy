#!/usr/bin/env python3

import subprocess

# Check if all nessecary packages are installed and install the missing ones
try:
    packages = ["python3-netifaces", "python3-dnspython", "python3-pexpect", "python3-psutil"]
    missing = [pkg for pkg in packages if subprocess.run(["dpkg", "-s", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0]
    if missing:
        subprocess.run(["apt", "-y", "install"] + missing, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    sys.exit(f"Exception: {str(e)}")

import argparse
import dns.resolver
import ipaddress
import netifaces
import os
import pexpect
import psutil
import re
import signal
import sys

debug = 1

# Check if a string is a valid routable IP
def is_global_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_global:
            return "wan"
        return "lan"
    except Exception:
        pass

    return "none"

# Find the default interface
def get_default_nic():
    gws = netifaces.gateways()
    default_gateway = gws.get('default', {})
    if netifaces.AF_INET in default_gateway:
        return default_gateway[netifaces.AF_INET][1]
    elif netifaces.AF_INET6 in default_gateway:
        return default_gateway[netifaces.AF_INET6][1]
    return "none"

# Find the stable privacy IP of dev
def get_stable_ipv6(dev):
    try:
        result = subprocess.run(["ip", "-6", "addr", "show", "dev", dev, "scope", "global", "mngtmpaddr"], capture_output=True, text=True, check=True)

        for line in result.stdout.strip().splitlines():
            if line:
                line = line.strip()

            if not line:
                continue

            match = re.search(r"^\s*inet6\s+([0-9a-fA-F:]+)/\d+", line)
            if match:
                return match.group(1)
    except Exception:
        pass

    sys.exit(f"Failed to find a stable privacy IP on dev {dev}")

# Get IPs for a given hostname, which can then be tested to find out if they are on the LAN or not
def resolve_host(hostname):

    res = dns.resolver.Resolver()
    res.timeout = 2
    res.lifetime = 5

    tried = set()

    def try_resolve(name):
        if name in tried:
            return "none"

        if debug > 0:
            print(f"Starting check for {name}...")

        tried.add(name)

        try:
            answers = res.resolve(name, dns.rdatatype.AAAA)
            if debug > 0:
                for rdata in answers:
                    print(f"Received the following answers: {rdata}")
            return [rdata.address for rdata in answers]
        except (dns.resolver.NoAnswer, dns.exception.Timeout):
            pass
        except dns.resolver.NXDOMAIN:
            return "none"

        try:
            answers = res.resolve(name, dns.rdatatype.A)
            if debug > 0:
                for rdata in answers:
                    print(f"Received the following answers: {rdata}")
            return [rdata.address for rdata in answers]
        except (dns.resolver.NoAnswer, dns.exception.Timeout):
            pass
        except dns.resolver.NXDOMAIN:
            return "none"

        try:
            answers = res.resolve(name, dns.rdatatype.CNAME)
            for rdata in answers:
                if debug > 0:
                    print(f"Received the following answers: {rdata}")
                return try_resolve(str(rdata.target).rstrip("."))
        except (dns.resolver.NoAnswer, dns.exception.Timeout):
            return "none"

        return "none"

    return try_resolve(hostname)

# Check to see if ip_host is a hostname or IP
def check_ip_host(ip_host):

    if ip_host:
        ip_host = ip_host.strip()

    if not ip_host:
        return False, None

    ip_check = is_global_ip(ip_host)
    if ip_check == "none":
        host_check = resolve_host(ip_host)
        if not host_check:
            return False, None

        return "host", host_check
    elif ip_check == False:
        return False, None

    return "ip", None

# Loop through commandline arguments to find hostnames and IPs
def check_host_or_ip(ssh_args):
    """
    Iterate over ssh_args, find first host/IP, check if LAN or global,
    and return:
        is_lan        : none, lan or wan depending if the host resolves only to LAN IPs
    """

    is_lan = "none"

    for arg in ssh_args:
        if arg:
            arg = arg.strip()

        if not arg:
            continue

        if debug > 0:
            print(f"Checking {arg}...")

        if arg.startswith("-"):
            continue

        ip_host, dns_records = check_ip_host(arg)

        if debug > 0:
            print(f"ip_host: {ip_host}...")

        if ip_host == "ip":
            ret = is_global_ip(arg)
            if ret in ("lan", "wan"):
                is_lan = ret
                break

        if ip_host == "host":
            for ip in dns_records:
                if debug > 0:
                    print(f"ip: {ip}...")

                ret = is_global_ip(ip)
                if debug > 0:
                    print(f"ret: {ret}...")

                if ret in ("lan", "wan"):
                    is_lan = ret
                    break

    return is_lan

def set_winsize(child):
    """Set window size of child pty to match the current terminal."""
    rows, cols = os.popen('stty size', 'r').read().split()
    child.setwinsize(int(rows), int(cols))

def sigwinch_passthrough(sig, data):
    set_winsize(child)

def main():
    # Load and parse commandline arguments
    parser = argparse.ArgumentParser(description="Wrapper around ssh that ensures a host/IP is provided.")
    parser.add_argument("-i", "--interface", default=None, help="Specify network interface")
    parser.add_argument("ssh_args", nargs=argparse.REMAINDER, help="Arguments passed to ssh (must include a hostname/IP)")
    args = parser.parse_args()

    # Check that there is at least one argument, presumably a hostname or IP
    if not args.ssh_args:
        sys.exit("Error: You must provide a hostname or IP for ssh.")

    # Check for a submitted network interface, otherwise get the default network interface
    dev = args.interface
    if not dev:
        dev = get_default_nic()

    if dev not in netifaces.interfaces():
        sys.exit("Error: {dev} isn't a valid interface.")

    iface_stat = False
    for iface, stats in psutil.net_if_stats().items():
        if iface == dev and stats.isup:
            iface_stat = True
            break

    if not iface_stat:
        sys.exit("Error: {dev} isn't up.")

    # Send all ssh args to find the hostname or IP to connect to
    is_lan = check_host_or_ip(args.ssh_args)
    if is_lan == "none":
        sys.exit("Error: You must provide a hostname or IP for ssh.")

    # Start building the ssh commandline arguments
    ssh_cmd = ["-tt"] + args.ssh_args

    # If connecting to a server not on the LAN bind to the network interface and IP
    if is_lan == "wan":
        stable_ip = get_stable_ipv6(dev)
        ssh_cmd += ["-B", dev]
        ssh_cmd += ["-b", stable_ip]

    if debug > 0:
        print(["ssh"] + ssh_cmd)

    # Everything should be good to connect now
    child = pexpect.spawn("ssh", args=ssh_cmd)
    set_winsize(child)
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)
    child.interact()

if __name__ == "__main__":
    main()
