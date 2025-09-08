import hashlib
import json
import argparse
import webbrowser
from flask import Flask, jsonify, request
import requests
from pathlib import Path

from TempMailGenerator.template import TEMPLATE

CONFIG_PATH = Path("config.json")
DEFAULT_CONFIG = {
    "rapid_api_keys": [
        "YOUR_API_KEY_1",
        "YOUR_API_KEY_2",
        "YOUR_API_KEY_3"
    ],
    "api_host": "temp-mail44.p.rapidapi.com",
    "api_base_url": "https://temp-mail44.p.rapidapi.com/api/v3"
}

if not CONFIG_PATH.exists():
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=4))

config = json.loads(CONFIG_PATH.read_text())

app = Flask(__name__)

API_KEYS = config["rapid_api_keys"]
KEY_INDEX = 0
TEMP_MAIL_HEADERS = {
    "content-type": "application/json",
    "X-RapidAPI-Key": API_KEYS[KEY_INDEX],
    "X-RapidAPI-Host": config["api_host"]
}

TEMP_NEW_MAIL_API = f"{config['api_base_url']}/email/new"
TEMP_READ_MAIL_API = f"{config['api_base_url']}/email/%s/messages"

class Email:
    def __init__(self, email: str, token: str):
        self.EMAIL = email
        self.TOKEN = token
        self.HASH = hashlib.md5(f"[{self.EMAIL}]:[{self.TOKEN}]".encode()).hexdigest()

    def read_inbox(self):
        response = requests.get(TEMP_READ_MAIL_API % self.EMAIL, headers=TEMP_MAIL_HEADERS)
        return response.json()

Emails = []

def generate_email():
    global KEY_INDEX
    TEMP_MAIL_HEADERS['X-RapidAPI-Key'] = API_KEYS[KEY_INDEX]
    response = requests.post(TEMP_NEW_MAIL_API, headers=TEMP_MAIL_HEADERS)
    data = response.json()
    if not data.get("email"):
        KEY_INDEX += 1
        if KEY_INDEX >= len(API_KEYS):
            return data
        return generate_email()
    email_obj = Email(data['email'], data['token'])
    Emails.append(email_obj)
    return email_obj

@app.route('/')
def index():
    return TEMPLATE

@app.route('/generate')
def generate():
    email = generate_email()
    return jsonify({"email": email.EMAIL, "token": email.HASH})

@app.route('/inbox')
def inbox():
    token = request.args.get('tk')
    email = next((e for e in Emails if e.HASH == token), None)
    if email is None:
        return jsonify({"messages": []})
    return jsonify({"messages": list(reversed(email.read_inbox()))})

def main():
    parser = argparse.ArgumentParser(
        description="Temporary Email Generator (Flask-based)",
        epilog="Example: python main.py --host 0.0.0.0 --port 8080 --no-browser"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5555, help="Port number (default: 5555)")
    parser.add_argument("--no-browser", action="store_true", help="Disable auto-opening the browser")
    parser.add_argument("--config", action="store_true", help="Edit configuration file (config.json)")

    args = parser.parse_args()

    if args.config:
        print("Current configuration:")
        print(json.dumps(config, indent=4))
        key_list = input("Enter new API keys (comma separated) or leave empty to keep: ").strip()
        if key_list:
            config["rapid_api_keys"] = [k.strip() for k in key_list.split(",")]
        new_host = input(f"API Host [{config['api_host']}]: ").strip()
        if new_host:
            config["api_host"] = new_host
        new_base = input(f"API Base URL [{config['api_base_url']}]: ").strip()
        if new_base:
            config["api_base_url"] = new_base
        CONFIG_PATH.write_text(json.dumps(config, indent=4))
        print("Configuration updated!")
        return

    if not args.no_browser:
        webbrowser.open(f"http://{args.host}:{args.port}/")

    app.run(debug=True, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
