from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import pyotp
import requests
import os

app = Flask(__name__)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    username = data['username']

    # Communicate with the user service to get user data
    response = requests.get(f'{USER_SERVICE_URL}/user/{username}')
    if response.status_code != 200:
        return jsonify({'message': 'User not found'}), 404

    user_data = response.json()['user']

    otp_secret = user_data.get('otp_secret')
    if not otp_secret:
        otp_secret = pyotp.random_base32()
        # Update the user's otp_secret in the user service
        requests.put(f'{USER_SERVICE_URL}/user/{username}', json={'otp_secret': otp_secret})

    otp = pyotp.TOTP(otp_secret).now()

    # Send email with OTP
    msg = Message('Your 2FA code', sender=app.config['MAIL_USERNAME'], recipients=[user_data['email']])
    msg.body = f'Your 2FA code is {otp}'
    mail.send(msg)

    return jsonify({'message': 'OTP sent'})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    username = data['username']
    otp = data['otp']

    # Communicate with the user service to get user data
    response = requests.get(f'{USER_SERVICE_URL}/user/{username}')
    if response.status_code != 200:
        return jsonify({'message': 'User not found'}), 404

    user_data = response.json()['user']
    otp_secret = user_data.get('otp_secret')

    if not otp_secret:
        return jsonify({'message': '2FA not enabled for this user'}), 400

    if pyotp.TOTP(otp_secret).verify(otp):
        return jsonify({'message': 'OTP verified'})
    else:
        return jsonify({'message': 'Invalid OTP'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5003)
