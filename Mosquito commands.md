## How to get a list of current topics

```
mosquitto_sub -v -u mqtt_username -P mqtt_password -t "#" -W 1 | while read topic payload; do echo "Topic: $topic"; done
```

## Listen for packets and output via jq for prettier display or output the raw packet

```
mosquitto_sub -v -u mqtt_username -P mqtt_password -t "#" | while read topic payload; do echo "Topic: $topic"; echo "$payload" | jq . 2>/dev/null || echo "$payload"; echo -e "---\n\n"; done
```
