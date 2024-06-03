# Using flask to make an api
# import necessary libraries and functions
# import openai
from openai import OpenAI
# We can use Flask to create a web server that can handle file uploads.
from flask import Flask, request
import os
import time

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
# After installing the OpenAI package, we will load the API key and create an OpenAI client.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# creating a Flask app
app = Flask(__name__)

@app.route('/api/v1/documentQuestionAndAnswer', methods=['POST'])
def documentQuestionAndAnswer():
    if 'file' not in request.files:
        files_not_attached = {
            'code': 'DRS/PDF001',
            'message': 'File not attached.',
            'status_code': 400,
            'detail': 'A PDF Document is not attached to the request.'
        }
        error_response = files_not_attached
        return error_response, error_response['status_code']

    file = request.files['file']
    prompt = request.args.get('question')
    current_directory = os.getcwd()

    # Concatenate the current directory with the filename to get the absolute path
    file_path = os.path.join(current_directory, file.filename)

    # Now you can save the file to the desired location
    file.save(file_path)
    pdf_path = file_path

    # Let's start by loading the pdf file to the client using the files .create method.
    file = client.files.create(
        file=open(file.filename, 'rb'),
        purpose="assistants"
    )

    # Create a thread with a user message and attached file. A conversation session between an Assistant and a user
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": prompt, "file_ids": [file.id]}])
    thread_id = thread.id

    # Initiate the conversation thread with OpenAI's assistant.
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id="asst_No5KPp3sh55uq4iMqQsTCexh",
        model="gpt-4-1106-preview",
        tools=[{"type": "retrieval"}])
    run_id = run.id

    # Check the status of the conversation thread.
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread_id, run_id=run_id)

    while (run_status.status != "completed"):
        run_status = client.beta.threads.runs.retrieve(
        thread_id=thread_id, run_id=run_id)
        time.sleep(2)

    # And finally, we can display the message and the response by the assistant.
    response = client.beta.threads.messages.list(thread_id=thread_id)
    try:
        if response.data:
            # Return the bot responses as JSON
            return {"response": response.data[0].content[0].text.value}
        else:
            return "something went wrong"
    except:
        return "something went wrong"
    finally:
        print('finally')
        os.remove(pdf_path)
        OpenAI(api_key=os.getenv("OPENAI_API_KEY")).files.delete(file.id)


# driver function
if __name__ == '__main__':
    app.run(debug=True)
