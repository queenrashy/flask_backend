import os

import jwt
from app import db
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class Domains(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    domain_name = db.Column(db.String(50))
    price = db.Column(db.Integer)
    registration_date = db.Column(db.DateTime, default=datetime.now)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(10))
    user = relationship("User", back_populates="domains")

    def __repr__(self):
        return f"<Domain {self.domain_name}>"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(200), unique=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(200))
    created = db.Column(db.DateTime, default=datetime.now)
    domains = relationship("Domains", back_populates="user")


    def __repr__(self):
        return f"<User {self.id}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self):
        expiration_time = datetime.now() + timedelta(days=10)
        payload = {
            'id': self.id,
            'exp': expiration_time
        }
        token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')
        return token

    @staticmethod
    def verify_auth_token(token):
        if not token:
            return None
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
            user = User.query.get(payload['id'])
            return user
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
            return None
        except jwt.DecodeError:
            print("Token is invalid.")
            return None
