
from flask import jsonify, request
from app import app, db
from models import User
from toolz import is_valid_email
from werkzeug.security import generate_password_hash


@app.route('/signup', methods=['POST'])
def sign_up():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    # check names
    if first_name is None or len(first_name) < 2:
        return jsonify({'error': 'Please enter a valid name!'}), 400

    # check if email is valid
    if not is_valid_email(email):
        return jsonify({'error': 'Please enter a valid email address!'}), 400
    
    # Check if email is unique
    exists = User.query.filter(User.email == email).first()
    if exists is not None:
        return jsonify({'error': 'Email already exists'}), 400
    
    # check password
    if password is None or len(password) < 6:
        return jsonify({'error': 'Password is invalid, please enter 6 or more characters.'}), 400
    
    # create user account
    new_user = User(first_name=first_name, last_name=last_name, email=email, phone=phone)
    db.session.add(new_user)
    new_user.set_password(password)

    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'User signup error: {e}'}), 400


@app.route('/login')
def login_user():
    email = request.json.get('email')
    password = request.json.get('password')

    if email is None or password is None:
        return jsonify({'error': 'Please enter email and password'}), 401
    
    if not is_valid_email(email):
        return jsonify({'error': 'Please enter a valid email address!'}), 400
    
    # find user
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({'error': 'User with this email does not exist'}), 401
    
    # validate password
    if user.check_password(password):
        # password is correct, generate jwt token
        token = user.generate_auth_token()
        return jsonify({'success': True, 'token': token})
    
    return jsonify({'error': 'Invalid email or password.'})
