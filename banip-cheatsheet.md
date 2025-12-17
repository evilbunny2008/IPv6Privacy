### Test dns
dig +noall +answer +time=5 +tries=5 openwrt.org A openwrt.org AAAA @1.1.1.1

### View all banned IPs
nft list table inet banIP

### White list an IP
uci add_list banip.global.allowlist_ipv4='104.18.8.193'

### Commit the allowlist IPs
uci commit banip

### after adding whitelist/blacklist (doesn't seem to happen via the webUI)
/etc/init.d/banip stop
/etc/init.d/banip start

### Manually remove an invalid DoH IP such as for downdetector.com.au
nft delete element inet banIP doh.v4 { 104.18.8.193 }
