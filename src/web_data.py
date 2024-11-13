import requests
import time

# Replace this function with radar data processing code
def get_radar_data(fall: bool):
    # This is simulated data; replace it with actual data from radar
    if fall:
        data = {
            "status": "fall_detected"  # Can be 'fall_detected' or 'no_fall'
        }
    else:
        data = {
            "status": "no_fall"  # Can be 'fall_detected' or 'no_fall'
        }
    return data


# Backend server URL
SERVER_URL = "http://138.197.73.178:5000/submit-data"  # Replace with the backend server IP

def push_radar_data(fall: bool):

    radar_data = get_radar_data(fall)

    try:
        # Send data to the backend
        response = requests.post(SERVER_URL, json=radar_data)
        if response.status_code == 200:
            print("Data sent successfully:", response.json())
        else:
            print("Failed to send data:", response.status_code)
    except Exception as e:
        print("Error:", e)
