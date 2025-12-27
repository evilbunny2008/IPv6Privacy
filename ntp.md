## How to get NTP working properly on SBCs with no hardware real time clock

### Disable other services that may interfere
```bash
systemctl disable --now systemd-timesyncd
systemctl mask systemd-timesyncd
apt -y purge fake-hwclock
```

### Install ntpsec packages
```bash
apt update && apt -y install ntpsec ntpsec-ntpdate ntpsec-ntpdig ntpstat
```

### Clean up
```bash
apt clean
```

### Add to the /etc/ntpsec/ntp.conf
```bash
echo "" >> /etc/ntpsec/ntp.conf
echo "# Fix system time no matter how much forward or backward the system time is" >> /etc/ntpsec/ntp.conf
echo "tinker panic 0" >> /etc/ntpsec/ntp.conf
```

### Add a check for during boot to fix any problems before the ntpsec daemon starts
```bash
echo "[Unit]
Description=One-shot NTP time sync
Before=ntpsec.service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/ntpdate -u 192.168.1.1

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/ntpdate-once.service
```

### Reload and restart everything
```bash
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable ntpdate-once
systemctl restart ntpsec ntpdate-once
```
