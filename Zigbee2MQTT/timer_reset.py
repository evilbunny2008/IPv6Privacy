#!/usr/bin/python3

import argparse
import configparser
import json
import os
import paho.mqtt.client as mqtt
import sys

from paho.mqtt.client import CallbackAPIVersion
from pprint import pprint

SENT_COUNTDOWN = False
SENT_COUNTDOWN_L1 = False
SENT_COUNTDOWN_L2 = False

def on_connect(client, userdata, flags, reason_code, properties):

    if DEBUG >= 1:
        print()
        print(f"Connected: reason_code={reason_code}, properties={properties}")

    client.subscribe(SUB_TOPIC)

    if DEBUG >= 1:
        print(f"Subscribed to {SUB_TOPIC}")
        print()

def parse_payload(payload):

    text = payload.decode("utf-8")

    if text == "ping":
        response = "pong"
        client.publish(PUB_TOPIC, "pong")
        return False, text

    try:
        data = json.loads(text)
        return True, data
    except json.JSONDecodeError:
        return False, text

def on_message(client, userdata, msg):

    global SENT_COUNTDOWN, SENT_COUNTDOWN_L1, SENT_COUNTDOWN_L2

    if not msg.topic.endswith("Taps"):
        return

    parsed, payload = parse_payload(msg.payload)

    if not parsed or not payload:
        return

    if DEBUG >= 2:
        print(f"Topic: {msg.topic}")
        pprint(payload)
        print()

    if "state" in payload and payload["state"] == "OFF":
        SENT_COUNTDOWN = False

    if "state_l1" in payload and payload["state_l1"] == "OFF":
        SENT_COUNTDOWN_L1 = False

    if "state_l2" in payload and payload["state_l2"] == "OFF":
        SENT_COUNTDOWN_L2 = False

    if "state" in payload and payload["state"] == "ON" and payload.get("countdown", 1440) <= 10 and not SENT_COUNTDOWN:
        SENT_COUNTDOWN = True
        client.publish(f"{msg.topic}/set", '{"state": "OFF"}')
        client.publish(f"{msg.topic}/set", '{"state": "ON", "countdown": 1440}')

        if DEBUG >= 1:
            print(f"Set {msg.topic} countdown to 1440")

    if "state_l1" in payload and payload.get("state_l1") == "ON" and payload.get("countdown_l1", 1440) <= 10 and not SENT_COUNTDOWN_L1:
        SENT_COUNTDOWN_L1 = True
        client.publish(f"{msg.topic}/set", '{"state_l1": "OFF"}')
        client.publish(f"{msg.topic}/set", '{"state_l1": "ON", "countdown_l1": 1440}')

        if DEBUG >= 1:
            print(f"Set {msg.topic} countdown_l1 to 1440")

    if "state_l2" in payload and payload.get("state_l2") == "ON" and payload.get("countdown_l2", 1440) <= 10 and not SENT_COUNTDOWN_L2:
        SENT_COUNTDOWN_L2 = True
        client.publish(f"{msg.topic}/set", '{"state_l2": "OFF"}')
        client.publish(f"{msg.topic}/set", '{"state_l2": "ON", "countdown_l2": 1440}')

        if DEBUG >= 1:
            print(f"Set {msg.topic} countdown_l2 to 1440")

print("Starting timer_reset.py...")

parser = argparse.ArgumentParser(description="Simple MQTT client to listen for Smart Water Valves when they have the physical button pushed to turn the 'tap' off and on to get round the 10 minute default limit")
parser.add_argument("-c", "--config", type = str, default="/etc/timer_reset.conf", help="Path to config file, /etc/timer_reset.conf is the default")
parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level (use -v, -vv, -vvv etc)')
args = parser.parse_args()

DEBUG = args.verbose

if(not os.path.exists(args.config) or not os.path.isfile(args.config)):
    print(f"Config file {args.config} doesn't exist.")
    sys.exit(1)

if(not os.access(args.config, os.R_OK)):
    print(f"Config file {args.config} isn't readable.")
    sys.exit(1)

configParser = configparser.ConfigParser(allow_no_value = True)
configParser.read(args.config)

hostname = configParser.get("MQTT", "hostname", fallback = "localhost")
port = configParser.getint("MQTT", "port", fallback = 1883)

username = configParser.get("MQTT", "username", fallback = None)
password = configParser.get("MQTT", "password", fallback = None)

SUB_TOPIC = configParser.get("MQTT", "topic", fallback = "zigbee2mqtt/#")

client = mqtt.Client(CallbackAPIVersion.VERSION2)

if username is not None and password is not None:
    client.username_pw_set(username, password)

client.on_connect = on_connect
client.on_message = on_message

client.connect(hostname, port, 60)
client.loop_forever()
