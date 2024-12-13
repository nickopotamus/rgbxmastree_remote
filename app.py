from flask import Flask, render_template, request
from tree import RGBXmasTree
from colorzero import Color
import threading
import subprocess
import os

app = Flask(__name__)
tree = RGBXmasTree()
lock = threading.Lock()

# Variable to track the currently running script
current_process = None

# Function to stop the currently running script
def stop_current_script():
    global current_process
    if current_process:
        current_process.terminate()
        current_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_color', methods=['POST'])
def set_color():
    stop_current_script()  # Stop any running scripts
    try:
        r = int(request.form['red'])
        g = int(request.form['green'])
        b = int(request.form['blue'])
        brightness = float(request.form['brightness'])
        color = Color(r / 255, g / 255, b / 255)

        selected_lights = request.form.getlist('light')  # Get list of selected lights
        with lock:
            if 'all' in selected_lights:
                tree.color = color
                tree.brightness = brightness
            else:
                for light in selected_lights:
                    tree[int(light)].color = color
                    tree[int(light)].brightness = brightness

        return f"Color set to RGB({r}, {g}, {b}) with brightness {brightness}", 200
    except Exception as e:
        return f"Error: {e}", 400

@app.route('/turn_off', methods=['POST'])
def turn_off():
    stop_current_script()  # Stop any running scripts
    with lock:
        tree.off()
    return "Tree turned off", 200

@app.route('/turn_on', methods=['POST'])
def turn_on():
    stop_current_script()  # Stop any running scripts
    with lock:
        tree.on()
    return "Tree turned on", 200

@app.route('/run_script', methods=['POST'])
def run_script():
    global current_process
    stop_current_script()  # Stop any running scripts

    try:
        script_name = request.form.get('script')  # Safely get the script name
        if not script_name:
            return "Error: Script name is required", 400

        script_path = f'./examples/{script_name}'
        # Check if the script exists before attempting to run it
        if not os.path.isfile(script_path):
            return f"Error: Script '{script_name}' not found", 400

        # Run the script as a subprocess
        current_process = subprocess.Popen(['python3', script_path])
        return f"Running script: {script_name}", 200
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
