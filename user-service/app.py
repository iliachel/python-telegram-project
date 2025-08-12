from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    otp_secret = db.Column(db.String(16))

from werkzeug.security import generate_password_hash

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})

@app.route('/user/<username>', methods=['GET', 'PUT'])
def user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'No user found!'})

    if request.method == 'GET':
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['email'] = user.email
        user_data['otp_secret'] = user.otp_secret
        return jsonify({'user': user_data})

    if request.method == 'PUT':
        data = request.get_json()
        user.otp_secret = data['otp_secret']
        db.session.commit()
        return jsonify({'message': 'User updated!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True, port=5001)
