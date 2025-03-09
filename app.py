from flask import Flask, jsonify, request
import requests
import threading
import time
import json

app = Flask(__name__)

@app.route('/achievements/summarize', methods=['POST'])
def submit():
    data = request.get_json()
    list_of_achievements = data.get("achievementDesc", [])
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
    headers = {"Content-Type": "application/json"}
    #external_api_url = "http://localhost:8081/hi"
    #response = requests.post(external_api_url, json=data)
    print("Call to external api completed", flush=True)

    # Send the response to the callback URL
    callback_url = data.get("callBackUrl")
    rated_achievements = []
    for ach in data.get("achievementDesc"):
        rated_achievements.append({
            "achievement": ach,
            "category": "Dummy Category",
            "rating": "3"
        })

    new_data = {
        "email": data.get("emailId"),
        "ratedAchievements": rated_achievements
    }
    json_new_data = json.dumps(new_data, indent=4)
    if callback_url:
        requests.post(callback_url, json=new_data, headers=headers)

if __name__ == '__main__':
    app.run(debug=True)