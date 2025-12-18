## Below is links to major reverse proxy IP ranges

### Cloudflare

Due to the sheer volume of traffic reverse proxied by Cloudflare, it's a bad idea to block any of their IPs except for their public resolver ranges 1.0.0.0/24, 1.1.1.0/24 and 2606:4700:4700::/48.

Below are links to plain text lists of their ranges excluding their public resolver IPs.

 - https://www.cloudflare.com/ips-v4/
 - https://www.cloudflare.com/ips-v6/

### Fastly

Fastly also proxies a large volume of traffic so it's not a good idea to try and block their IPs either, below is a link to a JSON formatted list

 - https://api.fastly.com/public-ip-list

### Other reverse proxy companies?

Please let me know of other reverse proxy companies!

## Blocking DoH/DoQ hostnames

### List of known hostnames that reply to DoH/DoQ requests

Since DoH/DoQ implementations usually rely on hostnames, rather than IPs, using the below list in Adguard Home/Pi-hole etc should be more effective at stopping DoH/DoQ DNS requests even being sent.

 - https://adguardteam.github.io/HostlistsRegistry/assets/filter_52.txt

### Additional DoH/DoQ hosts

 - ||dns.opendoh.com^$important
 - ||app.opendoh.com^$important
 - ||adblock.opendoh.com^$important
