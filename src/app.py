from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Function to generate random fake radar data
def generate_fake_fall_data():
    fall_status = random.choice(['fall_detected', 'no_fall'])
    fall_type = random.choice(['slip', 'trip', 'collapse']) if fall_status == 'fall_detected' else 'none'
    fall_severity = random.choice(['minor', 'moderate', 'severe']) if fall_status == 'fall_detected' else 'none'
    timestamp = '2024-09-23T12:00:00'
    return {
        'status': fall_status,
        'fall_type': fall_type,
        'fall_severity': fall_severity,
        'timestamp': timestamp
    }

# Route to serve radar data
@app.route('/radar-data', methods=['GET'])
def get_radar_data():
    fake_data = generate_fake_fall_data()
    return jsonify(fake_data)

if __name__ == '__main__':
    app.run(debug=True)