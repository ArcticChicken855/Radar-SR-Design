import requests


to_send = {'status':  'fall_detected'}

response = requests.post('http://localhost:5000/submit-data', json=to_send)
print(response)
