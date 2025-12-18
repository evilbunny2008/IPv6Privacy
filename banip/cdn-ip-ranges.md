## Below is links to major reverse proxy IP ranges

### Cloudflare

Due to the sheer volume of traffic reverse proxied by Cloudflare, it's a bad idea to block any of their IPs except for their public resolver ranges 1.0.0.0/24, 1.1.1.0/24 and 2606:4700:4700::/48.

Below are links to plain text lists of their ranges excluding their public resolver IPs.

 - https://www.cloudflare.com/ips-v4/
 - https://www.cloudflare.com/ips-v6/

### Fastly

Fastly also proxies a large volume of traffic so it's not a good idea to try and block their IPs either, below is a link to a JSON formatted list

 - https://api.fastly.com/public-ip-list (in json format)

### Other reverse proxy companies?

Please let me know of other reverse proxy companies!

## Blcoking known DoH/DoQ hostnames

Since DoH implementations rely on hostnames, rather than IPs, using the below list in Adguard Home/Pihole etc may be a much more effective method of stopping DoH/DoQ DNS requests

 - https://adguardteam.github.io/HostlistsRegistry/assets/filter_52.txt
