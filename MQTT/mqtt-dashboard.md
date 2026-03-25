# MQTT Dashboard examples for Zigbee2MQTT

# Introduction

[MQTT](https://mqtt.org/) is a light weight protocol designed for Internet of Things devices, not just for home automation, but everything up to industrial automation.

This document assumes a MQTT server, such as [Mosquitto](https://mosquitto.org/), is setup, and you also have [Zigbee2MQTT](https://www.zigbee2mqtt.io/) sending and receiving MQTT messages, and you have MQTT Dashboard connected to that MQTT server.

[My GitHub repository](https://github.com/evilbunny2008/UsefulScriptsAndOtherTidbits/tree/main/MQTT) has configuration examples and useful things to know for [Debian 13/Trixie](https://www.debian.org/).

I found starting out with [MQTT Dashboard](https://play.google.com/store/apps/details?id=com.app.vetru.mqttdashboard) to be a little daunting, mainly due to a lack of example configurations.

My hope is documenting examples will help people avoid corporate cloud services that have a tendency to be turned off, leaving them with expensive toys that instantly become useless.

## Adding a soil moisture sensor

Zigbee based [soil moisture sensors](https://www.aliexpress.com/item/1005008987466283.html) are incredibly good value for money and provide temperature, humidity and soil moisture readings.

It's advisable to set a friendly names for your devices in the Zigbee2MQTT web interface to memorable ones instead, such as 'SoilSensor1' for a soil moisture sensor.

To do this, go to the device section, then click on the current friendly name on the left side of the device table.

Then click on the edit icon next to the friendly name.

By default this will be 0x followed by a hex string which can be used if you don't change it.

### From the MQTT Dashboard home screen

Click on the '+' button toward the bottom right of the screen.

Select 'Create Widget'.

Enter a label for your widget in the 'Name' text box, for example 'GardenBed1' and then pick a widget group such as 'Backyard'.

### Displaying humidity from the sensor

Touch on 'Text' in the 'Widget Properties' section.

Type a name for the reading in the 'Name' text box, such as 'Humidity'.

For 'Type' select 'Numeric'.

Then set the 'Icon' to the picture of the rain drop with a percentage symbol, it's toward the bottom of all the icons, as this will be for humidity then click 'OK' at the bottom.

Then set a colour if you wish.

Make sure 'Broker' is set to the MQTT broker you added when setting up MQTT Dashboard.

For 'Subscription' you need to set this to 'zigbee2mqtt/' and the device's friendly name in Zigbee2MQTT, so in this case it would be 'zigbee2mqtt/SoilSensor1'.

Tick the 'JsonPath parse data' check box, then in the 'JsonPath parse data (payload)' text box set it to '$.humidity'.

For 'Decimal places' set this to '0'

Click 'Done'

### Displaying moisture from the sensor

Click on the '+' button under the 'Widget Properties' section.

Enter a name for the reading, such as 'Moisture'.

For 'Type' select 'Numeric'.

Set the 'Icon' to the same rain drop with the percentage symbol.

The rest of the details should be pre-filled from the humidity settings.

Again tick the 'JsonPath parse data' check box, then in the 'JsonPath parse data (payload)' text box set it to '$.soil_moisture'.

For 'Decimal places' set this to '0'

Click 'Done'

### Displaying temperature from the sensor

Click on the '+' button under the 'Widget Properties' section.

Enter a name for the reading, such as 'Temperature'.

For 'Type' select 'Numeric'.

Set the 'Icon' to the thermometer symbol on the second row, I then set the colour to black as the icon defaults to red.

The rest of the details should be pre-filled from the humidity settings.

Again tick the 'JsonPath parse data' check box, then in the 'JsonPath parse data (payload)' text box set it to '$.temperature'.

For 'Decimal places' set this to '1'

Click 'Done'

### Displaying LQI from the sensor (optional)

I found it useful to use the 4th and final box to show the LQI reported by the sensor as this will give visual feed back if the placement of the sensor is too far from your Zigbee co-ordinator or router.

Click on the '+' button under the 'Widget Properties' section.

Enter a name for the reading, such as 'LQI'.

For 'Type' select 'Numeric'.

Set the 'Icon' to the signal symbol on the right side of the top row, the icon defaults to red so feel free to change the colour if that doesn't suit.

The rest of the details should be pre-filled from the humidity settings.

Again tick the 'JsonPath parse data' check box, then in the 'JsonPath parse data (payload)' text box set it to '$.linkquality'.

For 'Decimal places' set this to '0'

Click 'Done'

### Once all boxes have been set

Just click 'Done' and it will take you back to the home screen hopefully showing you the current readings.

## Adding a device that does more than broadcast sensor information

Unlike soil moisture sensors, other devices such as Zigbee based [smart water timers](https://www.aliexpress.com/item/1005009335943136.html) can be used as taps to turn water on and off. This functionality requires addiitonal details in the sending section.

As with the soil moisture sensor it's worth while setting a friendly name for the device to something friendlier like 'GardenTap'.

### From the MQTT Dashboard home screen

From the home screen click on the '+' button toward the bottom right of the screen.

Select 'Create Widget'.

Enter a label for your widget in the 'Name' text box such as 'GardenTap' and then pick a widget group such as 'Backyard'.

### Adding a switch to turn water on and off remotely

Touch on 'Text' in the 'Widget Properties' section.

Type a name for the reading in the 'Name' text box, such as 'Tap' or 'LeftOutlet' if you have a device with more than one outlet.

For 'Type' select 'Switch'.

For 'Status Icon "On"' there isn't a suitable tap or water icon available, so I picked the power plug icon which can be found on the second last row.

For 'Status Icon "On"' I picked the power plug icon which is crossed out and it can be found on the second last row next to the power plug icon.

For 'Subscription' in this case it would be 'zigbee2mqtt/GardenTap'.

Tick the 'JsonPath parse data' check box, then in the 'JsonPath parse data (payload)' text box set it to '$.state'. If you have more than one outlet you may need to use '$.state_l1' or similar instead.

In the sending section, make sure 'Send topic same as subscription topic' is unticked.

Set the 'Send Topic' to 'zigbee2mqtt/GardenTap/set'

If your smart water timer has more than one outlet you may need to use 'state_l1' instead of 'state' below, and 'state_l2' for the 2nd outlet.

Zigbee2MQTT expects commands to be JSON formatted, so set 'Prefix' to '{"state": "'. Then set 'Suffix' to be '"}'. This is so when MQTT Dashboard transmits an 'ON' command the message body is {"state": "ON"}.

Note: For JSON to be valid you must only use double quotes for the prefix and suffix.

You can leave 'On' set to 'ON' and 'Off' set to 'OFF'.

Click 'Done'

You can then add another outlet or just click 'Done'.

Your should now see one or more switches on the home screen and touching on them should activate the solenoid in the device.

## Debugging

While MQTT dashboard does offer access to some MQTT messages, it seems to be restricted to configured widgets and values, rather than finding what topics to subscribe to.

Using the `mosquitto_sub` program you can listen for complete MQTT messages, this can be useful for identifying the actual device names Zigbee2MQTT uses.

### Listening for all messages under the zigbee2mqtt topic

```
mosquitto_sub -v -u "<mqtt_username>" -P "<mqtt_password>" -h "<server_ip>" -p <server_port> -t "zigbee2mqtt/#"
```

### Listening for all messages from a sub-topic or device

Zigbee2MQTT can be a bit noisy with status messages, so to only view messages from your device you do the following:

```
mosquitto_sub -v -u "<mqtt_username>" -P "<mqtt_password>" -h "<server_ip>" -p <server_port> -t "zigbee2mqtt/SoilSensor1/#"
```

### Example Zigbee2MQTT output

```
zigbee2mqtt/bridge/state {"state":"online"}
```
