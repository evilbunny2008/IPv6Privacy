# How to install and run Zigbee2MQTT

## Download the latest version from GitHub
mkdir -p /opt/zigbee2mqtt
git clone --depth 1 https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt

## Debian nodejs packages are too old, need to get nodejs packages from their repo
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
apt install -y nodejs

## Run npm so it does it's thing
cd /opt/zigbee2mqtt
npm ci

## Start zigbee2mqtt
Z2M_WATCHDOG=default node index.js
