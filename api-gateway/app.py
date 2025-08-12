from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import jwt
from functools import wraps

app = Flask(__name__)
# Allow requests from our React frontend, with credentials
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key')

# Service URLs from environment variables
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL')
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL')
TFA_SERVICE_URL = os.environ.get('TFA_SERVICE_URL')
TELEGRAM_SERVICE_URL = os.environ.get('TELEGRAM_SERVICE_URL')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/register', methods=['POST'])
def register():
    # Frontend will send JSON
    data = request.get_json()
    response = requests.post(f'{USER_SERVICE_URL}/register', json=data)
    return response.json(), response.status_code

@app.route('/api/login', methods=['POST'])
def login():
    # Frontend will send JSON
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    response = requests.post(f'{AUTH_SERVICE_URL}/login', auth=(username, password))

    if response.status_code == 200:
        token = response.json().get('token')
        resp = jsonify({'status': 'success', 'username': username})
        resp.set_cookie('token', token, httponly=True, samesite='Lax')
        return resp

    return response.json(), response.status_code

@app.route('/api/logout', methods=['POST'])
def logout():
    resp = jsonify({'status': 'success'})
    resp.delete_cookie('token')
    return resp

@app.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    # This endpoint can be used by the frontend to check if a user is logged in
    return jsonify({'username': current_user})


@app.route('/api/2fa/generate', methods=['POST'])
@token_required
def generate_2fa(current_user):
    response = requests.post(f'{TFA_SERVICE_URL}/generate', json={'username': current_user})
    return response.content, response.status_code

@app.route('/api/2fa/verify', methods=['POST'])
@token_required
def verify_2fa(current_user):
    response = requests.post(f'{TFA_SERVICE_URL}/verify', json={'username': current_user, 'otp': request.get_json()['otp']})
    return response.content, response.status_code

# --- Telegram Routes ---

@app.route('/api/telegram/send_message', methods=['POST'])
@token_required
def telegram_send_message(current_user):
    data = request.get_json()
    response = requests.post(f'{TELEGRAM_SERVICE_URL}/send_message', json=data)
    return response.json(), response.status_code

@app.route('/api/telegram/chat_history', methods=['GET'])
@token_required
def telegram_chat_history(current_user):
    response = requests.get(f'{TELEGRAM_SERVICE_URL}/chat_history')
    return response.json(), response.status_code

@app.route('/api/telegram/broadcast', methods=['POST'])
@token_required
def telegram_broadcast(current_user):
    data = request.get_json()
    message_text = data.get('text')
    if not message_text:
        return jsonify({'status': 'error', 'message': 'Message text is required'}), 400

    # Get all users from the telegram-service
    try:
        response = requests.get(f'{TELEGRAM_SERVICE_URL}/users')
        response.raise_for_status()
        user_ids = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': f'Could not get users from telegram-service: {e}'}), 500

    # Send message to each user
    success_count = 0
    failure_count = 0
    for user_id in user_ids:
        try:
            res = requests.post(f'{TELEGRAM_SERVICE_URL}/send_message', json={'user_id': user_id, 'text': message_text})
            if res.status_code == 200:
                success_count += 1
            else:
                failure_count += 1
        except requests.exceptions.RequestException:
            failure_count += 1

    return jsonify({'status': 'success', 'sent': success_count, 'failed': failure_count})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
