import re
import html
import time
from functools import wraps
from flask import request, jsonify, g, current_app
from typing import Optional, List
import hashlib
import secrets

class SecurityMiddleware:
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\b\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"])",
        r"(UNION\s+SELECT)",
        r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP))",
        r"('\s*(OR|AND)\s*')",
        r"(EXEC\s*\()",
        r"(xp_cmdshell)",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<form[^>]*>",
        r"expression\s*\(",
        r"vbscript:",
        r"data:text/html",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e/",
        r"\.\.%2f",
        r"%2e%2e%5c",
    ]

    @staticmethod
    def sanitize_input(data: str) -> str:
        if not isinstance(data, str):
            return data
        sanitized = html.escape(data, quote=True)
        return sanitized

    @staticmethod
    def detect_sql_injection(data: str) -> bool:
        if not isinstance(data, str):
            return False
        data_lower = data.lower()
        for pattern in SecurityMiddleware.SQL_INJECTION_PATTERNS:
            if re.search(pattern, data_lower, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def detect_xss(data: str) -> bool:
        if not isinstance(data, str):
            return False
        data_lower = data.lower()
        for pattern in SecurityMiddleware.XSS_PATTERNS:
            if re.search(pattern, data_lower, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def detect_path_traversal(data: str) -> bool:
        if not isinstance(data, str):
            return False
        data_lower = data.lower()
        for pattern in SecurityMiddleware.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, data_lower, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def validate_request_data(data, max_depth: int = 10, current_depth: int = 0) -> tuple:
        if current_depth > max_depth:
            return False, "Maximum nesting depth exceeded"

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(key, str):
                    if SecurityMiddleware.detect_sql_injection(key):
                        return False, f"Potential SQL injection detected in key: {key}"
                    if SecurityMiddleware.detect_xss(key):
                        return False, f"Potential XSS detected in key: {key}"

                if isinstance(value, str):
                    if SecurityMiddleware.detect_sql_injection(value):
                        return False, f"Potential SQL injection detected"
                    if SecurityMiddleware.detect_xss(value):
                        return False, f"Potential XSS detected"
                    if SecurityMiddleware.detect_path_traversal(value):
                        return False, f"Potential path traversal detected"
                elif isinstance(value, (dict, list)):
                    valid, msg = SecurityMiddleware.validate_request_data(value, max_depth, current_depth + 1)
                    if not valid:
                        return False, msg

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    if SecurityMiddleware.detect_sql_injection(item):
                        return False, "Potential SQL injection detected"
                    if SecurityMiddleware.detect_xss(item):
                        return False, "Potential XSS detected"
                elif isinstance(item, (dict, list)):
                    valid, msg = SecurityMiddleware.validate_request_data(item, max_depth, current_depth + 1)
                    if not valid:
                        return False, msg

        return True, None

class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.blocked_ips = {}

    def _get_client_ip(self) -> str:
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return request.remote_addr or 'unknown'

    def _get_rate_limit_key(self, identifier: str) -> str:
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    def is_rate_limited(self, identifier: Optional[str] = None, limit: int = 60, window: int = 60) -> tuple:
        if identifier is None:
            identifier = self._get_client_ip()

        current_time = time.time()
        key = self._get_rate_limit_key(identifier)

        if key in self.blocked_ips:
            if current_time < self.blocked_ips[key]:
                return True, 0
            else:
                del self.blocked_ips[key]

        if key not in self.requests:
            self.requests[key] = []

        self.requests[key] = [t for t in self.requests[key] if current_time - t < window]

        if len(self.requests[key]) >= limit:
            retry_after = int(window - (current_time - self.requests[key][0]))
            return True, retry_after

        self.requests[key].append(current_time)
        return False, 0

    def cleanup_expired(self, window: int = 60):
        current_time = time.time()
        for key in list(self.requests.keys()):
            self.requests[key] = [t for t in self.requests[key] if current_time - t < window]
            if not self.requests[key]:
                del self.requests[key]

rate_limiter = RateLimiter()

def rate_limit(limit: int = 60, window: int = 60, key_func=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = None
            if key_func:
                identifier = key_func()
            else:
                identifier = rate_limiter._get_client_ip()

            is_limited, retry_after = rate_limiter.is_rate_limited(identifier, limit, window)

            if is_limited:
                response = jsonify({
                    'code': 429,
                    'message': 'Too many requests. Please try again later.',
                    'data': {'retry_after': retry_after}
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(retry_after)
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = '0'
                return response

            response = f(*args, **kwargs)

            if hasattr(response, 'headers'):
                remaining = limit - len(rate_limiter.requests.get(rate_limiter._get_rate_limit_key(identifier), []))
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = str(max(0, remaining))

            return response
        return decorated_function
    return decorator

def validate_input(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json:
            data = request.get_json(silent=True)
            if data:
                valid, error_msg = SecurityMiddleware.validate_request_data(data)
                if not valid:
                    return jsonify({
                        'code': 400,
                        'message': error_msg or 'Invalid input data',
                        'data': None
                    }), 400

        for key, value in request.args.items():
            if SecurityMiddleware.detect_sql_injection(value) or SecurityMiddleware.detect_xss(value):
                return jsonify({
                    'code': 400,
                    'message': 'Invalid query parameter',
                    'data': None
                }), 400

        return f(*args, **kwargs)
    return decorated_function

def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

def add_security_headers(app):
    @app.after_request
    def after_request(response):
        return security_headers(response)
