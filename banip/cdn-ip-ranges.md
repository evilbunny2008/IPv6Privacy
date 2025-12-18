## Below is links to major reverse proxy IP ranges

### Cloudflare
 - https://www.cloudflare.com/ips-v4/
 - https://www.cloudflare.com/ips-v6/

Due to the sheer volumes of traffic proxied by Cloudflare it's not a good idea to block any of their IPs except 1.0.0.0/24, 1.1.1.0/24 and 2606:4700:4700::/48

## Fastly
 - https://api.fastly.com/public-ip-list (in json format)

Fastly also proxies a large volume of traffic so it's not a good idea to try and block their IPs either
