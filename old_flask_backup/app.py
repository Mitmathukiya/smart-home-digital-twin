from flask import Flask, render_template, request, jsonify
import logging

# Initialize the Flask Application
app = Flask(__name__)

# Set up some basic logging so we can see what's happening in the terminal
logging.basicConfig(level=logging.INFO)

# --- 1. SERVE THE FRONTEND ---
@app.route('/')
def home():
    """
    This tells Python: When a user goes to http://127.0.0.1:5000/, 
    look inside the 'templates' folder and send them the index.html file.
    """
    return render_template('index.html')

# --- 2. THE HARDWARE API ENDPOINT ---
@app.route('/control', methods=['POST'])
def control_device():
    """
    This is the listener. When the JavaScript does a fetch('/control'),
    it lands here. Python unpacks the data and decides what to do.
    """
    try:
        # Get the JSON data sent from the JavaScript
        data = request.get_json()
        device = data.get('device')
        action = data.get('action')

        # --- THIS IS WHERE YOU CONNECT PHYSICAL HARDWARE ---
        app.logger.info(f"⚡ HARDWARE COMMAND RECEIVED -> Device: {device} | Action: {action}")
        
        # Example: If you had real MQTT hardware, you would add logic here:
        # if device == 'light1':
        #     mqtt_client.publish("home/livingroom/light", action)
        # elif device == 'ac1':
        #     send_ir_signal(action)

        # Send a success response back to the JavaScript
        return jsonify({
            "status": "success", 
            "message": f"Command {action} sent to {device}",
            "device": device,
            "command": action
        }), 200

    except Exception as e:
        app.logger.error(f"Error processing command: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 3. RUN THE SERVER ---
if __name__ == '__main__':
    # host='0.0.0.0' allows other devices on your Wi-Fi to see it
    # port=5000 is the standard Flask port
    app.run(host='0.0.0.0', port=5000, debug=True)