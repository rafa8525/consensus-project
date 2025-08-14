from common.twilio_guard import send_sms
from flask import Flask, request, jsonify
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Explicitly specify the path to the .env file in the same directory as this script
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TARGET_PHONE_NUMBER = os.getenv('TARGET_PHONE_NUMBER')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

@app.route('/send_sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    # Require secret token for security
    if WEBHOOK_SECRET and data.get('secret') != WEBHOOK_SECRET:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    message_body = data.get('message', 'Test message from AI!')
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = clientsend_sms(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=TARGET_PHONE_NUMBER
        )
        return jsonify({'status': 'success', 'sid': message.sid}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Do not use app.run(); WSGI handles running the app on PythonAnywhere
