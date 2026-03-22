"""
JWT Authentication Handler
Production-grade JWT implementation with comprehensive security features
"""

import os
import jwt
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app, g
from typing import Optional, Dict, Any, Tuple
from cryptography.fernet import Fernet
import redis
import json

logger = logging.getLogger(__name__)


class JWTHandler:
    """
    Production-grade JWT Handler with:
    - Token rotation
    - Blacklist support
    - Redis-backed session management
    - Multiple token types (access, refresh, api-key)
    """

    def __init__(self):
        self.secret_key = self._get_secret_key()
        self.algorithm = os.environ.get('JWT_ALGORITHM', 'HS256')
        self.access_token_expires = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
        self.refresh_token_expires = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
        self.issuer = os.environ.get('JWT_ISSUER', 'interest-social-api')
        self.audience = os.environ.get('JWT_AUDIENCE', 'interest-social-users')
        self.token_prefix = 'Bearer '
        
        # Redis for token blacklist and session management
        self._init_redis()
        
        # Token encryption for sensitive data
        self._init_encryption()

    def _get_secret_key(self) -> str:
        """Securely retrieve JWT secret key"""
        secret = os.environ.get('JWT_SECRET_KEY')
        if not secret:
            logger.error("JWT_SECRET_KEY not set in environment")
            raise ValueError("JWT_SECRET_KEY must be set")
        if len(secret) < 32:
            logger.warning("JWT_SECRET_KEY should be at least 32 characters")
        return secret

    def _init_redis(self):
        """Initialize Redis connection for token management"""
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established for JWT management")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory fallback: {e}")
            self.redis_client = None
            self._blacklist = set()
            self._sessions = {}

    def _init_encryption(self):
        """Initialize encryption for sensitive token data"""
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate a temporary key (not recommended for production)
            logger.warning("ENCRYPTION_KEY not set, using temporary key")
            self.cipher = Fernet(Fernet.generate_key())

    def generate_access_token(
        self, 
        user_id: int, 
        additional_claims: Optional[Dict] = None,
        device_info: Optional[Dict] = None
    ) -> str:
        """
        Generate a secure access token
        
        Args:
            user_id: Unique user identifier
            additional_claims: Optional custom claims
            device_info: Device fingerprint for security
        """
        now = datetime.utcnow()
        jti = secrets.token_urlsafe(32)
        
        payload = {
            'sub': str(user_id),
            'iat': now,
            'exp': now + timedelta(seconds=self.access_token_expires),
            'iss': self.issuer,
            'aud': self.audience,
            'type': 'access',
            'jti': jti,
            'ver': '1.0',
        }
        
        if additional_claims:
            # Encrypt sensitive claims
            for key, value in additional_claims.items():
                if key in ['email', 'phone', 'ssn']:
                    payload[f'enc_{key}'] = self._encrypt_value(str(value))
                else:
                    payload[key] = value
        
        if device_info:
            payload['device_hash'] = self._hash_device_info(device_info)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Store session in Redis
        self._store_session(user_id, jti, 'access', now + timedelta(seconds=self.access_token_expires))
        
        logger.info(f"Access token generated for user {user_id}, jti: {jti[:16]}...")
        return token

    def generate_refresh_token(self, user_id: int, access_token_jti: Optional[str] = None) -> str:
        """Generate a refresh token with binding to access token"""
        now = datetime.utcnow()
        jti = secrets.token_urlsafe(32)
        
        payload = {
            'sub': str(user_id),
            'iat': now,
            'exp': now + timedelta(seconds=self.refresh_token_expires),
            'iss': self.issuer,
            'aud': self.audience,
            'type': 'refresh',
            'jti': jti,
            'access_jti': access_token_jti,  # Bind to access token
            'ver': '1.0',
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token with longer TTL
        self._store_session(user_id, jti, 'refresh', now + timedelta(seconds=self.refresh_token_expires))
        
        logger.info(f"Refresh token generated for user {user_id}, jti: {jti[:16]}...")
        return token

    def generate_api_key(self, user_id: int, name: str, scopes: list = None) -> Tuple[str, str]:
        """
        Generate a long-lived API key
        
        Returns:
            Tuple of (plain_key, key_hash) - only return plain_key once
        """
        prefix = 'isk_live_'
        random_part = secrets.token_urlsafe(32)
        api_key = f"{prefix}{random_part}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),
            'iat': now,
            'iss': self.issuer,
            'aud': self.audience,
            'type': 'api_key',
            'key_hash': key_hash[:16],
            'name': name,
            'scopes': scopes or ['read'],
            'ver': '1.0',
        }
        
        # Store API key metadata in Redis (no expiration for API keys)
        if self.redis_client:
            key = f"apikey:{key_hash}"
            self.redis_client.hset(key, mapping={
                'user_id': user_id,
                'name': name,
                'scopes': json.dumps(scopes or ['read']),
                'created_at': now.isoformat(),
                'last_used': now.isoformat(),
                'usage_count': 0
            })
        
        logger.info(f"API key generated for user {user_id}, name: {name}")
        return api_key, key_hash

    def decode_token(self, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    'require_exp': verify_exp,
                    'require_iat': True,
                    'require_iss': True,
                    'require_sub': True,
                    'verify_exp': verify_exp,
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

    def verify_access_token(self, token: str, check_blacklist: bool = True) -> Dict[str, Any]:
        """Verify an access token with comprehensive checks"""
        result = self.decode_token(token)
        
        if not result['valid']:
            return result
        
        payload = result['payload']
        
        # Check token type
        if payload.get('type') != 'access':
            return {'valid': False, 'error': 'Invalid token type', 'code': 'INVALID_TOKEN_TYPE'}
        
        # Check blacklist
        if check_blacklist:
            jti = payload.get('jti')
            if jti and self._is_blacklisted(jti):
                return {'valid': False, 'error': 'Token has been revoked', 'code': 'TOKEN_REVOKED'}
        
        # Check version
        if payload.get('ver') != '1.0':
            return {'valid': False, 'error': 'Invalid token version', 'code': 'INVALID_VERSION'}
        
        # Decrypt sensitive claims
        decrypted_claims = {}
        for key, value in payload.items():
            if key.startswith('enc_'):
                decrypted_claims[key[4:]] = self._decrypt_value(value)
        
        result['payload'].update(decrypted_claims)
        
        return result

    def verify_refresh_token(self, token: str, expected_access_jti: Optional[str] = None) -> Dict[str, Any]:
        """Verify a refresh token"""
        result = self.decode_token(token)
        
        if not result['valid']:
            return result
        
        payload = result['payload']
        
        if payload.get('type') != 'refresh':
            return {'valid': False, 'error': 'Invalid token type', 'code': 'INVALID_TOKEN_TYPE'}
        
        # Check if refresh token is blacklisted
        jti = payload.get('jti')
        if jti and self._is_blacklisted(jti):
            return {'valid': False, 'error': 'Refresh token has been revoked', 'code': 'TOKEN_REVOKED'}
        
        # Verify binding to access token (if provided)
        if expected_access_jti and payload.get('access_jti') != expected_access_jti:
            return {'valid': False, 'error': 'Token binding mismatch', 'code': 'BINDING_MISMATCH'}
        
        return result

    def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Verify an API key"""
        if not api_key.startswith('isk_live_'):
            return {'valid': False, 'error': 'Invalid API key format', 'code': 'INVALID_FORMAT'}
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if self.redis_client:
            key = f"apikey:{key_hash}"
            metadata = self.redis_client.hgetall(key)
            
            if not metadata:
                return {'valid': False, 'error': 'API key not found', 'code': 'KEY_NOT_FOUND'}
            
            # Update usage statistics
            self.redis_client.hincrby(key, 'usage_count', 1)
            self.redis_client.hset(key, 'last_used', datetime.utcnow().isoformat())
            
            return {
                'valid': True,
                'user_id': int(metadata.get('user_id')),
                'scopes': json.loads(metadata.get('scopes', '[]')),
                'name': metadata.get('name')
            }
        else:
            # Fallback for non-Redis environments
            return {'valid': False, 'error': 'API key verification unavailable', 'code': 'SERVICE_UNAVAILABLE'}

    def revoke_token(self, jti: str, user_id: int, token_type: str = 'access') -> bool:
        """Revoke a token by adding it to blacklist"""
        try:
            if self.redis_client:
                # Add to blacklist with TTL matching token expiration
                key = f"blacklist:{jti}"
                ttl = self.access_token_expires if token_type == 'access' else self.refresh_token_expires
                self.redis_client.setex(key, ttl, 'revoked')
                
                # Also add to user's revoked tokens list
                user_key = f"user:{user_id}:revoked"
                self.redis_client.sadd(user_key, jti)
                self.redis_client.expire(user_key, max(self.access_token_expires, self.refresh_token_expires))
            else:
                self._blacklist.add(jti)
            
            logger.info(f"Token revoked: {jti[:16]}... for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            return False

    def revoke_all_user_tokens(self, user_id: int) -> bool:
        """Revoke all tokens for a user (force logout everywhere)"""
        try:
            if self.redis_client:
                # Get all active sessions for user
                pattern = f"session:{user_id}:*"
                sessions = self.redis_client.keys(pattern)
                
                for session_key in sessions:
                    jti = session_key.decode().split(':')[-1] if isinstance(session_key, bytes) else session_key.split(':')[-1]
                    self.revoke_token(jti, user_id)
                
                # Clear all user sessions
                self.redis_client.delete(f"user:{user_id}:sessions")
            
            logger.info(f"All tokens revoked for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke user tokens: {e}")
            return False

    def rotate_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Rotate tokens - issue new access and refresh tokens, revoke old ones"""
        result = self.verify_refresh_token(refresh_token)
        
        if not result['valid']:
            return result
        
        payload = result['payload']
        user_id = int(payload['sub'])
        old_jti = payload['jti']
        
        # Revoke old refresh token
        self.revoke_token(old_jti, user_id, 'refresh')
        
        # Generate new tokens
        new_access_token = self.generate_access_token(user_id)
        new_refresh_token = self.generate_refresh_token(user_id)
        
        # Decode to get new JTI
        new_access_payload = self.decode_token(new_access_token)
        
        return {
            'valid': True,
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'Bearer',
            'expires_in': self.access_token_expires
        }

    def _store_session(self, user_id: int, jti: str, token_type: str, expires: datetime):
        """Store session information"""
        try:
            if self.redis_client:
                session_key = f"session:{user_id}:{jti}"
                ttl = int((expires - datetime.utcnow()).total_seconds())
                self.redis_client.setex(session_key, ttl, token_type)
                
                # Add to user's sessions set
                user_sessions_key = f"user:{user_id}:sessions"
                self.redis_client.sadd(user_sessions_key, jti)
        except Exception as e:
            logger.warning(f"Failed to store session: {e}")

    def _is_blacklisted(self, jti: str) -> bool:
        """Check if a token is blacklisted"""
        try:
            if self.redis_client:
                return self.redis_client.exists(f"blacklist:{jti}") > 0
            return jti in self._blacklist
        except Exception:
            return False

    def _hash_device_info(self, device_info: Dict) -> str:
        """Create a hash of device information for binding"""
        device_str = json.dumps(device_info, sort_keys=True)
        return hashlib.sha256(device_str.encode()).hexdigest()[:16]

    def _encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value"""
        return self.cipher.encrypt(value.encode()).decode()

    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value"""
        return self.cipher.decrypt(encrypted_value.encode()).decode()

    def get_active_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user"""
        try:
            if self.redis_client:
                pattern = f"session:{user_id}:*"
                sessions = self.redis_client.keys(pattern)
                return [s.decode().split(':')[-1] if isinstance(s, bytes) else s.split(':')[-1] for s in sessions]
            return []
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []


# Global JWT handler instance
jwt_handler = JWTHandler()


def jwt_required(f=None, optional: bool = False, scopes: list = None):
    """
    Decorator to protect routes with JWT authentication

    Args:
        optional: If True, don't require authentication but populate g.user if available
        scopes: Required scopes for API key authentication
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            api_key_header = request.headers.get('X-API-Key')

            g.user = None
            g.auth_type = None

            # Try API Key first
            if api_key_header:
                result = jwt_handler.verify_api_key(api_key_header)
                if result['valid']:
                    # Check scopes
                    if scopes:
                        user_scopes = result.get('scopes', [])
                        if not all(scope in user_scopes for scope in scopes):
                            return jsonify({
                                'code': 403,
                                'message': 'Insufficient scope',
                                'data': None
                            }), 403

                    g.user = {'id': result['user_id']}
                    g.auth_type = 'api_key'
                    g.scopes = result.get('scopes', [])
                    return f(*args, **kwargs)
                elif not optional:
                    return jsonify({
                        'code': 401,
                        'message': result.get('error', 'Invalid API key'),
                        'data': None
                    }), 401

            # Try JWT Bearer token
            if auth_header:
                if not auth_header.startswith(jwt_handler.token_prefix):
                    if not optional:
                        return jsonify({
                            'code': 401,
                            'message': 'Invalid authorization header format',
                            'data': None
                        }), 401
                else:
                    token = auth_header[len(jwt_handler.token_prefix):]
                    result = jwt_handler.verify_access_token(token)

                    if result['valid']:
                        g.user = {
                            'id': int(result['payload']['sub']),
                            'jti': result['payload'].get('jti'),
                            'claims': result['payload']
                        }
                        g.auth_type = 'jwt'
                        g.token = token
                        return f(*args, **kwargs)
                    elif not optional:
                        return jsonify({
                            'code': 401,
                            'message': result.get('error', 'Invalid token'),
                            'data': {'code': result.get('code')}
                        }), 401

            if optional:
                return f(*args, **kwargs)

            return jsonify({
                'code': 401,
                'message': 'Authentication required',
                'data': None
            }), 401

        return decorated_function

    if f is not None and callable(f):
        # Used as @jwt_required without parentheses
        return decorator(f)
    else:
        # Used as @jwt_required() with parentheses
        return decorator


def require_scope(*required_scopes):
    """Decorator to require specific scopes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_scopes = getattr(g, 'scopes', [])
            
            if not all(scope in user_scopes for scope in required_scopes):
                return jsonify({
                    'code': 403,
                    'message': f'Required scope(s): {", ".join(required_scopes)}',
                    'data': None
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
