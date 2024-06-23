from flask import Blueprint, jsonify, request, current_app

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/health')
def health():
    try:
        return jsonify({'healthy': True}), 200
    except:
        return jsonify({'healthy': False}), 500