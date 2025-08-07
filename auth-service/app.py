from flask import Flask, request, jsonify
import jwt
import datetime
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-secret-key'
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL')

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify'}), 401

    # Communicate with the user service to get user data
    response = requests.get(f'{USER_SERVICE_URL}/user/{auth.username}')
    if response.status_code != 200:
        return jsonify({'message': 'Could not verify'}), 401

    user_data = response.json()['user']

    if check_password_hash(user_data['password'], auth.password):
        token = jwt.encode({'user': user_data['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return jsonify({'message': 'Could not verify'}), 401

from werkzeug.security import check_password_hash

if __name__ == '__main__':
    app.run(debug=True, port=5002)
