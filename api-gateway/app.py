from flask import Flask, request, jsonify, redirect, url_for, make_response
import requests
import os
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-secret-key'
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL')
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL')
TFA_SERVICE_URL = os.environ.get('TFA_SERVICE_URL')

def get_current_user():
    token = request.headers.get('Authorization')
    if not token:
        return None
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return data['user']
    except:
        return None

@app.route('/register', methods=['POST'])
def register():
    # The browser sends form data, not JSON.
    # We read from request.form and convert it to JSON for the user-service.
    form_data = request.form.to_dict()
    response = requests.post(f'{USER_SERVICE_URL}/register', json=form_data)

    if response.status_code == 200:
        # In a real app, we might add a flash message here.
        # For now, just redirect to the login page.
        return redirect(url_for('catch_all', path='login'))

    # If there was an error, return the error message from the user-service
    return response.content, response.status_code

@app.route('/login', methods=['POST'])
def login():
    # The browser sends form data. The auth-service expects HTTP Basic Auth.
    # We extract the form data and pass it as the 'auth' tuple to requests.
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    response = requests.post(f'{AUTH_SERVICE_URL}/login', auth=(username, password))

    if response.status_code == 200:
        token = response.json().get('token')
        # Redirect to the admin page, setting the token in an HttpOnly cookie
        resp = make_response(redirect(url_for('catch_all', path='admin')))
        resp.set_cookie('token', token, httponly=True, samesite='Lax')
        return resp

    # If there was an error, return the error message from the auth-service
    return response.content, response.status_code

@app.route('/2fa/generate', methods=['POST'])
def generate_2fa():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'Not authorized'}), 401

    response = requests.post(f'{TFA_SERVICE_URL}/generate', json={'username': current_user})
    return response.content, response.status_code

MONOLITH_SERVICE_URL = os.environ.get('MONOLITH_SERVICE_URL')

@app.route('/2fa/verify', methods=['POST'])
def verify_2fa():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'Not authorized'}), 401

    response = requests.post(f'{TFA_SERVICE_URL}/verify', json={'username': current_user, 'otp': request.get_json()['otp']})
    return response.content, response.status_code

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    response = requests.get(f'{MONOLITH_SERVICE_URL}/{path}')
    return response.content, response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
