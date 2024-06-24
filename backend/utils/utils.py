import bcrypt
import jwt
from functools import wraps
from flask import request, jsonify


JWT_KEY = "JWT_Private_Key"

def hash_password(password):
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return salt, hash_password


def check_password(password, hashedPassword):
    if bcrypt.checkpw(password.encode('utf-8'), hashedPassword):
        return True
    return False


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing"}), 403
        
        try:
            payload = jwt.decode(token, JWT_KEY, "HS256")
            user_id = payload["user_id"]
            if not user_id:
                return jsonify({"message": "Invalid token!"}), 403
        except Exception as e:
            return jsonify({"message": "Something went wrong!"}), 403
        return f(user_id, *args, **kwargs)
    return decorated