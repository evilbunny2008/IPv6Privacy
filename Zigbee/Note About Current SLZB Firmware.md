# Note About Current SLZB Firmware

Firmware SLZB released in March 2026 is buggy and Zigbee2MQTT will lose, but not be aware, it's connection to my SLZB-06U has been lost, so won't reconnect automatically either.

Version SLZB-OS 3.2.6.dev0 with Coordinator firmware 20260307 are effected by this.

Rolling back to SLZB-OS v3.2.4 with Coordinator firmware 20250321 works

Just rolling back to those versions is not enough, you also need to make Zigbee2MQTT regenerate keys as well.

See this issue for more details https://github.com/Koenkk/zigbee2mqtt/issues/31329
