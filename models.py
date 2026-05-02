from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user') # 'admin' or 'user'
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    # --- Chaos Session Fields ---
    # Chaos parameters (u, xL, b, xG, y, xT, a, xS) string format mein
    chaos_params = db.Column(db.Text, nullable=True) 
    key_expiry = db.Column(db.DateTime, nullable=True)

    # --- Security & Recovery Fields ---
    q1 = db.Column(db.String(100), nullable=True) # Childhood Nickname
    q2 = db.Column(db.String(100), nullable=True) # Best Friend Name
    failed_attempts = db.Column(db.Integer, default=0)
    lock_until = db.Column(db.DateTime, nullable=True)

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Encrypted text
    enc_key = db.Column(db.Text, nullable=False)  # Encrypted key
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)