from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    otp_secret = db.Column(db.String(16))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if user.otp_secret:
                return redirect(url_for('login_2fa', user_id=user.id))
            else:
                login_user(user)
                return redirect(url_for('admin'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/login/2fa/<int:user_id>', methods=['GET', 'POST'])
def login_2fa(user_id):
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        otp = request.form['otp']
        if pyotp.TOTP(user.otp_secret).verify(otp):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Invalid OTP. Please try again.')

    # Send email with OTP
    otp = pyotp.TOTP(user.otp_secret).now()
    msg = Message('Your 2FA code', sender='your-email@example.com', recipients=[user.email])
    msg.body = f'Your 2FA code is {otp}'
    mail.send(msg)

    return render_template('login_2fa.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')

import requests

@app.route('/telegram_admin')
@login_required
def telegram_admin():
    return render_template('telegram_admin.html')

@app.route('/telegram/send_message', methods=['POST'])
@login_required
def telegram_send_message():
    data = request.get_json()
    response = requests.post('http://telegram-service:8002/send_message', json=data)
    return response.json()

@app.route('/telegram/chat_history')
@login_required
def telegram_chat_history():
    response = requests.get('http://telegram-service:8002/chat_history')
    return response.json()

@app.route('/2fa_setup', methods=['GET', 'POST'])
@login_required
def two_factor_setup():
    if request.method == 'POST':
        otp = request.form['otp']
        if pyotp.TOTP(current_user.otp_secret).verify(otp):
            flash('2FA setup successful!')
            return redirect(url_for('admin'))
        else:
            flash('Invalid OTP. Please try again.')

    if not current_user.otp_secret:
        current_user.otp_secret = pyotp.random_base32()
        db.session.commit()

    totp = pyotp.TOTP(current_user.otp_secret)
    uri = totp.provisioning_uri(name=current_user.username, issuer_name='Simple Web App')

    import qrcode
    import io
    import base64

    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    qr_code = base64.b64encode(buf.getvalue()).decode('ascii')

    return render_template('two_factor_setup.html', secret=current_user.otp_secret, qr_code=qr_code)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5005)
