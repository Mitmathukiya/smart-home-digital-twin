import paho.mqtt.client as mqtt
import time

# Device Configuration
DEVICE_ID = "light1"
COMMAND_TOPIC = f"home/{DEVICE_ID}/command"
STATUS_TOPIC = f"home/{DEVICE_ID}/status"

# Internal state of the light
current_state = "OFF"

# What to do when the device connects to the broker
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[{DEVICE_ID}] Connected to MQTT Broker!")
    # Start listening for incoming commands
    client.subscribe(COMMAND_TOPIC)
    print(f"[{DEVICE_ID}] Listening for commands on: {COMMAND_TOPIC}")
    
    # Announce initial status to the network
    client.publish(STATUS_TOPIC, current_state)

# What to do when a message arrives on a subscribed topic
def on_message(client, userdata, msg):
    global current_state
    
    # Decode the message and convert to uppercase (so "on" or "ON" both work)
    command = msg.payload.decode().upper()
    print(f"\n[{DEVICE_ID}] Incoming command received: {command}")

    # Process the command
    if command in ["ON", "OFF"]:
        if current_state == command:
            print(f"[{DEVICE_ID}] Light is already {current_state}. No change needed.")
        else:
            current_state = command
            print(f"[{DEVICE_ID}] Click! Turning {current_state}...")
            time.sleep(0.5) # Simulating the split-second it takes hardware to react
            
            # Announce the new status to the network
            client.publish(STATUS_TOPIC, current_state)
            print(f"[{DEVICE_ID}] Status updated to: {current_state}")
    else:
        print(f"[{DEVICE_ID}] Unknown command '{command}'. Ignoring.")

# Setup Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Connect and run
print(f"Starting {DEVICE_ID} simulator...")
client.connect("localhost", 1883, 60)

# loop_forever() keeps the script running endlessly until you press Ctrl+C
try:
    client.loop_forever()
except KeyboardInterrupt:
    print(f"\n[{DEVICE_ID}] Simulator shut down.")