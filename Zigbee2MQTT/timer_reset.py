#!/usr/bin/python3

import json
import paho.mqtt.client as mqtt

from paho.mqtt.client import CallbackAPIVersion
from pprint import pprint

BROKER = "localhost"
PORT = 1883
USERNAME = "username"
PASSWORD = "password"

SUB_TOPIC = "zigbee2mqtt/#"

SENT_COUNTDOWN = False
SENT_COUNTDOWN_L1 = False
SENT_COUNTDOWN_L2 = False

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected: reason_code={reason_code}, properties={properties}")
    client.subscribe(SUB_TOPIC)
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
        print("Set countdown to 1440")

    if "state_l1" in payload and payload.get("state_l1") == "ON" and payload.get("countdown_l1", 1440) <= 10 and not SENT_COUNTDOWN_L1:
        SENT_COUNTDOWN_L1 = True
        client.publish(f"{msg.topic}/set", '{"state_l1": "OFF"}')
        client.publish(f"{msg.topic}/set", '{"state_l1": "ON", "countdown_l1": 1440}')
        print("Set countdown_l1 to 1440")

    if "state_l2" in payload and payload.get("state_l2") == "ON" and payload.get("countdown_l2", 1440) <= 10 and not SENT_COUNTDOWN_L2:
        SENT_COUNTDOWN_L2 = True
        client.publish(f"{msg.topic}/set", '{"state_l2": "OFF"}')
        client.publish(f"{msg.topic}/set", '{"state_l2": "ON", "countdown_l2": 1440}')
        print("Set countdown_l2 to 1440")

client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="test-client")

client.username_pw_set(USERNAME, PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
