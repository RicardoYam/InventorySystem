from flask import Blueprint, jsonify, request, current_app
from models.models import db, User, UserRole
from utils.utils import hash_password, check_password, JWT_KEY
import jwt
import datetime

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/health')
def health():
    try:
        return jsonify({'healthy': True}), 200
    except:
        return jsonify({'healthy': False}), 500
    
    
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username and not password:
        return jsonify({"message": "Missing fields"}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User doesn't exist"}), 400
    
    if not check_password(password, user.password):
        return jsonify({"message": "Password incorrect"}), 400
    
    token = jwt.encode({"user_id": user.id,
                        "username": user.username,
                        "role": str(user.role)},
                        JWT_KEY)
    
    return jsonify({"message": "Login success", "username": user.username, "token": token}), 200
    

    
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username and not password:
        return jsonify({"message": "Missing fields"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
    
    salt, password = hash_password(password)

    if username == 'admin':
        new_user = User(username=username, salt=salt, password=password, role = UserRole.ADMIN)
    else:
        new_user = User(username=username, salt=salt, password=password, role = UserRole.USER)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 200