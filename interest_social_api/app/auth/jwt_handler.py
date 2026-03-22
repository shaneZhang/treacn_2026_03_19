import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from typing import Optional, Dict, Any

class JWTHandler:
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
        self.algorithm = os.environ.get('JWT_ALGORITHM', 'HS256')
        self.access_token_expires = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
        self.refresh_token_expires = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
        self.issuer = 'interest-social-api'
        self.audience = 'interest-social-users'

    def generate_access_token(self, user_id: int, additional_claims: Optional[Dict] = None) -> str:
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),
            'iat': now,
            'exp': now + timedelta(seconds=self.access_token_expires),
            'iss': self.issuer,
            'aud': self.audience,
            'type': 'access',
            'jti': secrets.token_urlsafe(16)
        }
        if additional_claims:
            payload.update(additional_claims)
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: int) -> str:
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),
            'iat': now,
            'exp': now + timedelta(seconds=self.refresh_token_expires),
            'iss': self.issuer,
            'aud': self.audience,
            'type': 'refresh',
            'jti': secrets.token_urlsafe(16)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    'require_exp': True,
                    'require_iat': True,
                    'require_iss': True,
                    'require_sub': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_iss': True,
                    'verify_aud': True
                }
            )
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token has expired', 'code': 'TOKEN_EXPIRED'}
        except jwt.InvalidIssuerError:
            return {'valid': False, 'error': 'Invalid token issuer', 'code': 'INVALID_ISSUER'}
        except jwt.InvalidAudienceError:
            return {'valid': False, 'error': 'Invalid token audience', 'code': 'INVALID_AUDIENCE'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': str(e), 'code': 'INVALID_TOKEN'}

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        result = self.decode_token(token)
        if result['valid']:
            if result['payload'].get('type') != 'access':
                return {'valid': False, 'error': 'Invalid token type', 'code': 'INVALID_TOKEN_TYPE'}
        return result

    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        result = self.decode_token(token)
        if result['valid']:
            if result['payload'].get('type') != 'refresh':
                return {'valid': False, 'error': 'Invalid token type', 'code': 'INVALID_TOKEN_TYPE'}
        return result

    def get_token_hash(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

jwt_handler = JWTHandler()

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'code': 401,
                'message': 'Authorization header is required',
                'data': None
            }), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'code': 401,
                'message': 'Invalid authorization header format. Use: Bearer <token>',
                'data': None
            }), 401

        token = parts[1]
        result = jwt_handler.verify_access_token(token)

        if not result['valid']:
            return jsonify({
                'code': 401,
                'message': result['error'],
                'data': {'code': result.get('code')}
            }), 401

        request.current_user_id = int(result['payload']['sub'])
        request.current_user = result['payload']

        return f(*args, **kwargs)
    return decorated_function

def optional_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
                result = jwt_handler.verify_access_token(token)
                if result['valid']:
                    request.current_user_id = int(result['payload']['sub'])
                    request.current_user = result['payload']
                else:
                    request.current_user_id = None
                    request.current_user = None
            else:
                request.current_user_id = None
                request.current_user = None
        else:
            request.current_user_id = None
            request.current_user = None
        return f(*args, **kwargs)
    return decorated_function
