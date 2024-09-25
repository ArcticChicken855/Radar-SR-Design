from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing
CORS(app)

# Store radar data with default value (no fall)
radar_data = {
    'status': 'no_fall'  # Either 'fall_detected' or 'no_fall'
}

# Route to handle POST requests from the Raspberry Pi
@app.route('/submit-data', methods=['POST'])
def receive_data():
    global radar_data
    radar_data = request.json  # Update radar_data with incoming JSON
    return jsonify({'message': 'Data received'}), 200

# Route to handle GET requests from React frontend
@app.route('/radar-data', methods=['GET'])
def get_radar_data():
    return jsonify(radar_data)  # Send radar_data to React frontend

# Start Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
