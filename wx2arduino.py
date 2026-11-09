import json
import math
import os
import threading
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import serial

# Latest value received for each reading, keyed by short name
latest = {}
lock = threading.Lock()


def topics():
    return {
        'T': os.getenv('TOPIC_TEMPERATURE'),
        'H': os.getenv('TOPIC_HUMIDITY'),
        'W': os.getenv('TOPIC_WIND'),
        'R': os.getenv('TOPIC_RAIN'),
    }


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("MQTT connection failed: {}".format(reason_code))
        return
    # Subscribe here so subscriptions are restored after a reconnect
    for topic in topics().values():
        client.subscribe(topic)


def send(ser):
    """Write the latest readings to the Arduino. Caller must hold the lock."""
    if len(latest) < 4:
        return  # Haven't heard every reading yet
    result = {
        "T": "{:d}".format(math.trunc(latest['T'])),
        "W": "{:d}".format(math.trunc(latest['W'])),
        "H": "{:d}".format(math.trunc(latest['H'])),
        "R": "{:1.2f}".format(latest['R'])
    }
    ser.write(json.dumps(result).encode('utf-8'))


def on_message(client, userdata, msg):
    ser, failed = userdata
    try:
        value = float(msg.payload.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return
    if not math.isfinite(value):
        return
    with lock:
        matched = False
        for key, topic in topics().items():
            if msg.topic == topic:
                latest[key] = value
                matched = True
        if not matched:
            return
        try:
            send(ser)  # New data arrived, refresh the display
        except serial.SerialException:
            failed.set()


def main():
    load_dotenv()
    try:
        ser = serial.Serial(os.getenv("SERIAL_PORT"))
    except serial.SerialException:
        print("Unable to open port")
        exit(1)

    failed = threading.Event()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=(ser, failed))
    username = os.getenv('MQTT_USER')
    if username:
        client.username_pw_set(username, os.getenv('MQTT_PASS'))
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(os.getenv('MQTT_HOST', 'localhost'),
                   int(os.getenv('MQTT_PORT', '1883')))
    client.loop_start()  # Handles network traffic and reconnects in a thread

    failed.wait()  # Run until a serial write fails
    client.loop_stop()
    exit(1)


if __name__ == "__main__":
    main()
