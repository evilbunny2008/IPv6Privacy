#META {"start":1}

# Heartbeat monitoring script that will reboot SLZB devices if no updates detected in MQTT for 30 minutes

import json
import MQTT

var HEARTBEAT_INTERVAL = 60                      # 60 seconds in ms
var last_heartbeat = 0
var last_z2m_seen = 0
var RESTART_TIMEOUT = 30 * HEARTBEAT_INTERVAL    # 30 mins no Z2M = restart

var logmsg = "Attempting to connect to MQTT server"
SLZB.log(logmsg)
MQTT.waitConnect(0xff)
var msg = {"connecting": logmsg}
MQTT.publish("connecting", json.dump(msg))
SLZB.log("Connected to MQTT broker")

# subscribe to all zigbee2mqtt messages to track activity
MQTT.subscribe("zigbee2mqtt/#")

def on_message(topic, data)
    # update last time we saw Z2M traffic
    last_z2m_seen = SLZB.millis() / 1000
end

MQTT.on_message(on_message)

while true
    # Convert to seconds or now will overflow after ~49 days of uptime
    var now = SLZB.millis() / 1000

    # send heartbeat
    if now - last_heartbeat >= HEARTBEAT_INTERVAL
        var msg = {"status": "online"}
        MQTT.publish("heartbeat", json.dump(msg))
        last_heartbeat = now
        SLZB.log("Heartbeat sent")
    end

    # check if Z2M has gone silent
    if last_z2m_seen > 0 && now - last_z2m_seen > RESTART_TIMEOUT
        var logmsg = "No Z2M traffic for 30 mins, rebooting..."
        SLZB.log(logmsg)
        var msg = {"alert": logmsg, "action": "rebooting", "timeout_minutes": 30}
        MQTT.publish("alert", json.dump(msg))
        last_z2m_seen = now  # prevent immediate re-trigger if reboot fails
        SLZB.delay(1000)
        SLZB.reboot()
    end

    SLZB.delay(10000) # Wait 10 seconds and check again
end
