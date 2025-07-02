import os
import random
from twilio.rest import Client

# Load environment variables from .env if needed (optional, depending on setup)
from dotenv import load_dotenv
load_dotenv()

# Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_from_number = os.getenv('TWILIO_PHONE_NUMBER') or '+18886607830'
user_to_number = os.getenv('USER_PHONE_NUMBER') or '+16502283267'  # Update if needed!

# Path to question bank
question_file = 'memory/proactive_questions_bank.md'

def get_random_questions(filepath, n=3):
    with open(filepath, 'r', encoding='utf-8') as f:
        questions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return random.sample(questions, min(n, len(questions)))

def send_sms(body):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=user_to_number,
        from_=twilio_from_number,
        body=body
    )
    print(f"Sent: {body}\nSID: {message.sid}")

if __name__ == '__main__':
    questions = get_random_questions(question_file, 3)
    for i, q in enumerate(questions, 1):
        send_sms(f"Q{i}: {q}")
