from flask import Flask, jsonify, request
import requests
import threading
import time

app = Flask(__name__)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})

@app.route('/achievements/summarize', methods=['POST'])
def submit():
    data = request.get_json()
    list_of_achievements = data.get("achievements", [])
    call_back_url = data.get("callBackUrl", "")
    email_id = data.get("emailId", "")
    reportType = data.get("type", "")
    print("Accepted summarize request for "+email_id, flush=True)
    
    # Start the process in a separate thread
    thread = threading.Thread(target=process_request, args=(data,))
    thread.start()

    # Return immediately to the Java API
    return jsonify({"message": "Processing started"}), 202

def process_request(data):
    """Handles the external API call and sends the result to the callback URL"""
    print("Calling ext api")
    external_api_url = "http://localhost:8081/hi"
    response = requests.post(external_api_url, json=data)
    time.sleep(10)
    print("Call to external api completed", flush=True)

    # Send the response to the callback URL
    callback_url = data.get("callBackUrl")
    if callback_url:
        requests.post(callback_url, json=response.json())

if __name__ == '__main__':
    app.run(debug=True)