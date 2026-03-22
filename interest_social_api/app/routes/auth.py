from flask import Blueprint, request, jsonify
from app.auth.jwt_handler import jwt_handler, jwt_required
from app.auth.crypto import password_handler, api_key_handler

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': 'Request body is required',
            'data': None
        }), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([username, email, password]):
        return jsonify({
            'code': 400,
            'message': 'Username, email and password are required',
            'data': None
        }), 400

    if len(password) < 8:
        return jsonify({
            'code': 400,
            'message': 'Password must be at least 8 characters long',
            'data': None
        }), 400

    password_hash, salt = password_handler.hash_password(password)

    return jsonify({
        'code': 200,
        'message': 'User registered successfully',
        'data': {
            'username': username,
            'email': email
        }
    })

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': 'Request body is required',
            'data': None
        }), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not all([username, password]):
        return jsonify({
            'code': 400,
            'message': 'Username and password are required',
            'data': None
        }), 400

    user_id = 1001

    access_token = jwt_handler.generate_access_token(user_id)
    refresh_token = jwt_handler.generate_refresh_token(user_id)

    return jsonify({
        'code': 200,
        'message': 'Login successful',
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': jwt_handler.access_token_expires
        }
    })

@auth_bp.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': 'Request body is required',
            'data': None
        }), 400

    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({
            'code': 400,
            'message': 'Refresh token is required',
            'data': None
        }), 400

    result = jwt_handler.verify_refresh_token(refresh_token)
    if not result['valid']:
        return jsonify({
            'code': 401,
            'message': result['error'],
            'data': None
        }), 401

    user_id = int(result['payload']['sub'])
    new_access_token = jwt_handler.generate_access_token(user_id)
    new_refresh_token = jwt_handler.generate_refresh_token(user_id)

    return jsonify({
        'code': 200,
        'message': 'Token refreshed successfully',
        'data': {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'Bearer',
            'expires_in': jwt_handler.access_token_expires
        }
    })

@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required
def logout():
    return jsonify({
        'code': 200,
        'message': 'Logout successful',
        'data': None
    })

@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required
def get_current_user():
    user_id = request.current_user_id
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'user_id': user_id
        }
    })

@auth_bp.route('/api/auth/api-keys', methods=['POST'])
@jwt_required
def create_api_key():
    api_key, key_hash = api_key_handler.generate_api_key()
    key_id = api_key_handler.generate_api_key_id()

    return jsonify({
        'code': 200,
        'message': 'API key created successfully',
        'data': {
            'key_id': key_id,
            'api_key': api_key,
            'warning': 'Store this API key securely. It will not be shown again.'
        }
    })
