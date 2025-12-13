#!/usr/bin/python3

#
# Simple script to generate a server key pair acceptable by Adguard Home and uhttpd running on OpenWRT
# Make sure you run ssl-ca.py first to generate the CA key and certificate, then you only need to import
# the CA certificate once in your browser to validate all subsequent server certificates
#
# Note: Adguard Home doesn't currectly accept/recognise ED25519/X25519 certificates and keys...
#

# To use the key and certificate in Adguard Home, just go into the webUI, open the "Settings" menu and select
# "Encryption settings" then scroll to the bottom of the page and select "aste the certificates contents" then
# paste the PEM encoded certificate into the box below. Then select "Paste the private key contents" and make sure
# the "Use the previously saved key" check box is unticked and paste the PEM encoded key into the box below.
#
# Because the CA certificate isn't signed by another CA already in one of the certificates in /etc/ssl/certs
# Adguard home will display a warning about not being able to verify the certificate, this is normal just
# click "Save configuration" button at the bottom left to enable it.
#
# Unfortunately the OpenWRT website doesn't have a webUI option to set/update the key pair like Adguard, so
# you need to ssh into the router using 'root' as the username and the webUI password for the password. Then
#
# echo "<paste server PEM certificate here>" > /etc/uhttpd.crt
# echo "<paste server PEM key here>" > /etc/uhttpd.key
# /etc/init.d/uhttpd restart
#
# And then your browser will no longer complain about invalid certificates
#

import datetime
import ipaddress
import os
import socket
import sys

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

#
# Set the CA PKI key pair file names the same as in ssl-ca.py
#
ca_file_crt = "ca_ec.crt"
ca_file_key = "ca_ec.key"

#
# Nothing else needs configuring below this line, hostnames and IPs are read from the command line instead of being hard coded
#

if not os.path.exists(ca_file_key) or not os.path.exists(ca_file_crt):
    print(f"{ca_file_key} or {ca_file_crt} doesn't exist, did you forget to run ssl-ca.py first?")
    sys.exit()

ca_key = None
with open(ca_file_key, "rb") as f:
    ca_key = serialization.load_pem_private_key(f.read(), password=None)

if not ca_key:
    print(f"There was a problem loading or parsing {ca_file_key}...")

ca_cert = None
with open(ca_file_crt, "rb") as f:
    ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

if not ca_cert:
    print(f"There was a problem reading or parsing {ca_file_crt}...")

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <hostname_or_ip> [<hostname_or_ip> ...]")
    sys.exit(1)

def getSAN(addr):
    try:
        # Try IPv4 or IPv6
        ip = ipaddress.ip_address(addr)
        return f"IP:{ip}"
    except ValueError:
        # Not an IP, treat as hostname
        try:
            # Try to resolve hostname (IPv4 or IPv6)
            info = socket.getaddrinfo(addr, None)
            # Pick first resolved IP for display
            resolved_ip = info[0][4][0]
            return f"DNS:{addr}"
        except socket.gaierror:
            return False

def outputCertDetails(cert):
    print("Certificate Details:")
    print("-------------------")

    # Subject
    print("Subject:", cert.subject.rfc4514_string())

    # Issuer
    print("Issuer:", cert.issuer.rfc4514_string())

    # Serial number
    print("Serial Number:", cert.serial_number)

    # Validity
    print("Not Before:", cert.not_valid_before_utc.astimezone())
    print("Not After :", cert.not_valid_after_utc.astimezone())

    # Signature algorithm
    print("Signature Algorithm OID:", cert.signature_algorithm_oid._name)

    # Public key info
    pubkey = cert.public_key()
    print("Public Key Type:", type(pubkey).__name__)
    if hasattr(pubkey, "public_bytes"):
        print("Public Key (PEM):")
        print(pubkey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode())

    # Extensions
    if cert.extensions:
        print("\nX.509v3 Extensions:")
        for ext in cert.extensions:
            print(f"- {ext.oid._name}: {ext.value}")

all_entries = []
for arg in sys.argv[1:]:
    ret = getSAN(arg)

    if not ret:
        continue

    if ret.startswith(("DNS:", "IP:")) and ret not in all_entries:
        all_entries.append(ret)

common_name = None
if all_entries:
    for entry in all_entries:
        if entry.startswith("DNS:"):
            common_name = entry[4:]
            break
        elif entry.startswith("IP:"):
            common_name = entry[3:]
            break

if not common_name:
    print("No hostname or IP found, won't continue")
    sys.exit()

#print(common_name)
#print(all_entries)
#sys.exit()

common_name_file = common_name.replace('.', '_').replace(':', '_')

server_ec_key = common_name_file + "_ec.key"
server_ec_crt = common_name_file + "_ec.crt"

#print(server_ec_key)
#print(server_ec_crt)
#sys.exit()

utc_now = datetime.datetime.now(datetime.timezone.utc)
valid_to = ca_cert.not_valid_after_utc

#print(utc_now)
#print(valid_to)
#sys.exit()

# Generate server key for certificate
server_key = ec.generate_private_key(ec.SECP256R1())

# Save server private key
with open(server_ec_key, "wb") as f:
    f.write(server_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Build server subject
server_subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])

# Build SAN list from all_entries
san_list = []
for entry in all_entries:
    if entry.startswith("DNS:"):
        hostname = entry[4:]  # Strip "DNS:"
        san_list.append(x509.DNSName(hostname))
    elif entry.startswith("IP:"):
        ip_str = entry[3:]  # Strip "IP:"
        # Convert to proper ipaddress object
        ip_obj = ipaddress.ip_address(ip_str)
        san_list.append(x509.IPAddress(ip_obj))

if not san_list:
    print("SAN list failed to build...")
    sys.exit()

#print(san_list)
#sys.exit()

# Build the certificate
server_cert = x509.CertificateBuilder()\
    .subject_name(server_subject)\
    .issuer_name(ca_cert.issuer)\
    .public_key(server_key.public_key())\
    .serial_number(x509.random_serial_number())\
    .not_valid_before(utc_now)\
    .not_valid_after(valid_to)\
    .add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False
    )\
    .sign(private_key=ca_key, algorithm=hashes.SHA512())

if not server_cert:
    print("Server Certificate failed to be issued...")
    sys.exit()

# Save certificate
with open(server_ec_crt, "wb") as f:
    f.write(server_cert.public_bytes(serialization.Encoding.PEM))

# Output debugging info
print("Generated:")
print("  - CA certificate subject: " + ca_cert.subject.rfc4514_string())
outputCertDetails(ca_cert)

print("\n  - Server key file: " + server_ec_key)
print(f"  - Server certificate: {server_ec_crt} Subject : " + server_cert.subject.rfc4514_string())

# Check cert details...
with open(server_ec_crt, "rb") as f:
    cert = x509.load_pem_x509_certificate(f.read(), default_backend())
    outputCertDetails(cert)
