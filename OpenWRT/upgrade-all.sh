#!/bin/sh

# From https://blog.lostgeek.net/upgrade-all-script-for-openwrt/

opkg update
upgradables=$(opkg list-upgradable | awk '{print $1}') || exit 0
[ -z "$upgradables" ] && echo "No packages to upgrade." && exit 0
echo "Upgrade: $upgradables"; read -p "Enter y/n: " r
[ "$r" = "y" ] && opkg upgrade $upgradables
