from flask import Flask, jsonify, request
import requests
#import threading
#import time
#import json
import ast
from google import genai
from google.genai import types

app = Flask(__name__)

client = genai.Client(api_key="none-of-your-business")
@app.route('/achievements/summarize', methods=['POST'])
def submit():
    data = request.get_json()
    email_id = data.get("emailId", "")
    print("Accepted summarize request for "+email_id, flush=True)
    
    # Start the process in a separate thread
    #thread = threading.Thread(target=process_request, args=(data,))
    #thread.start()
    process_request(data)

    # Return immediately to the Java API
    return jsonify({"message": "Processing started"}), 202

def process_request(data):
    
    """Handles the external API call and sends the result to the callback URL"""   
    
    # Get the prompt from the request
    list_of_achievements = data.get("achievementDesc", [])
    str_list_of_achievements = str(list_of_achievements)
    # Specify the path to your text file
    prompt_file_path = 'prompt.txt'

    # Read the contents of the prompt file into a string
    with open(prompt_file_path, 'r') as file:
        prompt_file_contents = file.read()

    # Specify the path to your evaluation framework JSON file
    file_path = 'evaluationFamework.json'

    # Read the contents of the JSON file into a string
    with open(file_path, 'r') as file:
        framework_json = file.read()

    # Replace '<Achievements>' with 'str_list_of_achievements'
    final_prompt = prompt_file_contents.replace('<Achievements>', str_list_of_achievements)
    final_prompt = final_prompt.replace('<Framework JSON>', framework_json)

    # print("--- Final prompt is: " + final_prompt)

    # Call the Gemini API to generate text
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=final_prompt
    )

    # Return the generated text as a JSON response
    # print("--- Response from AI is: " + response.text, flush=True)
    # Step 1: Remove the surrounding backticks and any leading/trailing whitespace
    cleaned_response = response.text.strip().strip('`')

    # Step 2: Optionally, you can also remove the "json" part if it's included
    if cleaned_response.startswith('json'):
        cleaned_response = cleaned_response[4:].strip()

    # If you want to parse it into a Python object
    json_data = ast.literal_eval(cleaned_response)


    # Send the response to the callback URL
    callback_url = data.get("callBackUrl")
    new_data = {
        "email": data.get("emailId"),
        "reportId": data.get("reportId"),
        "ratedAchievements": json_data
    }

    #print("--- Data to be posted is: " + str(new_data), flush=True)

    headers = {"Content-Type": "application/json"}
    if callback_url:
        requests.post(callback_url, json=new_data, headers=headers)

if __name__ == '__main__':
    app.run(debug=True)