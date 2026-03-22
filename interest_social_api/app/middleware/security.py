"""
Security Middleware
Comprehensive protection against common web attacks
"""

import re
import html
import time
import hashlib
import secrets
import logging
from functools import wraps
from flask import request, jsonify, g, current_app, Response
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """
    Comprehensive security middleware providing:
    - SQL Injection protection
    - XSS (Cross-Site Scripting) protection
    - CSRF (Cross-Site Request Forgery) protection
    - Path traversal protection
    - Rate limiting
    - Security headers
    - Input validation
    """

    # SQL Injection patterns - comprehensive list
    SQL_INJECTION_PATTERNS = [
        # Basic SQL keywords
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE|GRANT|REVOKE)\b)",
        # Comments
        r"(--|#|/\*|\*/)",
        # Boolean-based blind SQLi
        r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\b\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"])",
        # UNION-based SQLi
        r"(UNION\s+(ALL\s+)?SELECT)",
        # Stacked queries
        r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE))",
        # Time-based blind SQLi
        r"(WAITFOR\s+DELAY|BENCHMARK|SLEEP\s*\()",
        # Error-based SQLi
        r"(CONVERT\s*\(|CAST\s*\()",
        # Out-of-band SQLi
        r"(LOAD_FILE|INTO\s+(OUTFILE|DUMPFILE))",
        # Boolean operations
        r"('\s*(OR|AND)\s*')",
        # Stored procedures
        r"(EXEC\s*\(|EXECUTE\s*\()",
        # Extended stored procedures
        r"(xp_cmdshell|sp_oamethod|sp_oacreate)",
        # Hex encoding
        r"(0x[0-9a-fA-F]+)",
        # Char encoding
        r"(CHAR\s*\(\s*\d+)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        # Script tags
        r"<script[^>]*>.*?</script>",
        # JavaScript protocol
        r"javascript:",
        # Event handlers
        r"on\w+\s*=",
        # Data URIs
        r"data:text/html",
        r"data:image/svg\+xml",
        # VBScript
        r"vbscript:",
        # Expression
        r"expression\s*\(",
        # CSS imports
        r"@import",
        # Iframes
        r"<iframe[^>]*>",
        # Objects and embeds
        r"<object[^>]*>",
        r"<embed[^>]*>",
        # Forms
        r"<form[^>]*>",
        # Base tag
        r"<base[^>]*>",
        # Meta refresh
        r"<meta[^>]*http-equiv\s*=\s*['\"]refresh['\"]",
        # SVG with scripts
        r"<svg[^>]*>.*?<script",
        # Template literals (Angular, Vue, etc.)
        r"\{\{.*?\}\}",
        r"\$\{.*?\}",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e/",
        r"\.%2f",
        r"%2e%2e%5c",
        r"%252e%252e%252f",
        r"..%c0%af",
        r"..%c1%9c",
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`]\s*\w+",
        r"\$\(\s*\w+",
        r"`\s*\w+",
        r"\|\s*\w+",
    ]

    def __init__(self):
        self._compile_patterns()
        self._rate_limit_store = {}
        self._csrf_tokens = {}

    def _compile_patterns(self):
        """Compile regex patterns for performance"""
        self.sql_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS]
        self.xss_patterns = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.XSS_PATTERNS]
        self.path_patterns = [re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS]
        self.cmd_patterns = [re.compile(p, re.IGNORECASE) for p in self.COMMAND_INJECTION_PATTERNS]

    @staticmethod
    def sanitize_input(data: str, allow_markup: bool = False) -> str:
        """
        Sanitize user input to prevent XSS
        
        Args:
            data: Input string to sanitize
            allow_markup: If True, allow safe HTML (requires bleach)
        """
        if not isinstance(data, str):
            return data
        
        if allow_markup:
            try:
                import bleach
                allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
                allowed_attrs = {}
                return bleach.clean(data, tags=allowed_tags, attributes=allowed_attrs, strip=True)
            except ImportError:
                pass
        
        # Basic HTML escaping
        sanitized = html.escape(data, quote=True)
        return sanitized

    def detect_sql_injection(self, data: str) -> tuple:
        """
        Detect potential SQL injection attempts
        
        Returns:
            Tuple of (is_attack, matched_pattern)
        """
        if not isinstance(data, str):
            return False, None
        
        data_lower = data.lower()
        
        for i, pattern in enumerate(self.sql_patterns):
            if pattern.search(data_lower):
                return True, self.SQL_INJECTION_PATTERNS[i]
        
        return False, None

    def detect_xss(self, data: str) -> tuple:
        """
        Detect potential XSS attempts
        
        Returns:
            Tuple of (is_attack, matched_pattern)
        """
        if not isinstance(data, str):
            return False, None
        
        data_lower = data.lower()
        
        for i, pattern in enumerate(self.xss_patterns):
            if pattern.search(data_lower):
                return True, self.XSS_PATTERNS[i]
        
        return False, None

    def detect_path_traversal(self, data: str) -> tuple:
        """
        Detect path traversal attempts
        
        Returns:
            Tuple of (is_attack, matched_pattern)
        """
        if not isinstance(data, str):
            return False, None
        
        data_lower = data.lower()
        
        for i, pattern in enumerate(self.path_patterns):
            if pattern.search(data_lower):
                return True, self.PATH_TRAVERSAL_PATTERNS[i]
        
        return False, None

    def detect_command_injection(self, data: str) -> tuple:
        """
        Detect command injection attempts
        
        Returns:
            Tuple of (is_attack, matched_pattern)
        """
        if not isinstance(data, str):
            return False, None
        
        for i, pattern in enumerate(self.cmd_patterns):
            if pattern.search(data):
                return True, self.COMMAND_INJECTION_PATTERNS[i]
        
        return False, None

    def validate_request_data(self, data, max_depth: int = 10, current_depth: int = 0) -> tuple:
        """
        Recursively validate request data for security threats
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if current_depth > max_depth:
            return False, "Maximum nesting depth exceeded"
        
        if isinstance(data, dict):
            for key, value in data.items():
                # Check key
                if isinstance(key, str):
                    is_attack, pattern = self.detect_sql_injection(key)
                    if is_attack:
                        return False, f"Potential SQL injection detected in key: {key[:50]}"
                    
                    is_attack, pattern = self.detect_xss(key)
                    if is_attack:
                        return False, f"Potential XSS detected in key: {key[:50]}"
                
                # Check value
                result = self.validate_request_data(value, max_depth, current_depth + 1)
                if not result[0]:
                    return result
        
        elif isinstance(data, list):
            for item in data:
                result = self.validate_request_data(item, max_depth, current_depth + 1)
                if not result[0]:
                    return result
        
        elif isinstance(data, str):
            # SQL Injection check
            is_attack, pattern = self.detect_sql_injection(data)
            if is_attack:
                logger.warning(f"SQL injection detected: {pattern}")
                return False, "Potential SQL injection detected"
            
            # XSS check
            is_attack, pattern = self.detect_xss(data)
            if is_attack:
                logger.warning(f"XSS detected: {pattern}")
                return False, "Potential XSS detected"
            
            # Path traversal check
            is_attack, pattern = self.detect_path_traversal(data)
            if is_attack:
                logger.warning(f"Path traversal detected: {pattern}")
                return False, "Potential path traversal detected"
            
            # Command injection check
            is_attack, pattern = self.detect_command_injection(data)
            if is_attack:
                logger.warning(f"Command injection detected: {pattern}")
                return False, "Potential command injection detected"
        
        return True, None

    def check_csrf_token(self, request) -> bool:
        """
        Validate CSRF token for state-changing requests
        """
        # Skip for safe methods
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'TRACE']:
            return True
        
        # Get token from header
        token = request.headers.get('X-CSRF-Token')
        if not token:
            token = request.form.get('csrf_token')
        
        if not token:
            return False
        
        # Get session CSRF token
        session_token = getattr(g, 'csrf_token', None)
        if not session_token:
            return False
        
        # Constant-time comparison
        return secrets.compare_digest(token, session_token)

    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token"""
        token = secrets.token_urlsafe(32)
        g.csrf_token = token
        return token


# Global security middleware instance
security_middleware = SecurityMiddleware()


def add_security_headers(app):
    """Add comprehensive security headers to all responses"""
    
    @app.after_request
    def after_request(response):
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "media-src 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers['Content-Security-Policy'] = csp
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Clickjacking protection
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = (
            'accelerometer=(), '
            'camera=(), '
            'geolocation=(), '
            'gyroscope=(), '
            'magnetometer=(), '
            'microphone=(), '
            'payment=(), '
            'usb=()'
        )
        
        # Strict Transport Security (HSTS)
        if app.config.get('APP_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Remove server information
        response.headers.pop('Server', None)
        response.headers.pop('X-Powered-By', None)
        
        return response


def validate_input(f):
    """Decorator to validate all input data for security threats"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Validate query parameters
        for key, value in request.args.items():
            is_valid, error = security_middleware.validate_request_data({key: value})
            if not is_valid:
                logger.warning(f"Security threat detected in query param: {key}")
                return jsonify({
                    'code': 400,
                    'message': 'Invalid input detected',
                    'data': None
                }), 400
        
        # Validate form data
        if request.form:
            for key, value in request.form.items():
                is_valid, error = security_middleware.validate_request_data({key: value})
                if not is_valid:
                    logger.warning(f"Security threat detected in form data: {key}")
                    return jsonify({
                        'code': 400,
                        'message': 'Invalid input detected',
                        'data': None
                    }), 400
        
        # Validate JSON body
        if request.is_json:
            try:
                data = request.get_json()
                if data:
                    is_valid, error = security_middleware.validate_request_data(data)
                    if not is_valid:
                        logger.warning(f"Security threat detected in JSON body: {error}")
                        return jsonify({
                            'code': 400,
                            'message': 'Invalid input detected',
                            'data': None
                        }), 400
            except Exception as e:
                logger.warning(f"Failed to parse JSON: {e}")
                return jsonify({
                    'code': 400,
                    'message': 'Invalid JSON',
                    'data': None
                }), 400
        
        # Validate path parameters
        for key, value in kwargs.items():
            is_valid, error = security_middleware.validate_request_data({key: value})
            if not is_valid:
                logger.warning(f"Security threat detected in path param: {key}")
                return jsonify({
                    'code': 400,
                    'message': 'Invalid input detected',
                    'data': None
                }), 400
        
        return f(*args, **kwargs)
    return decorated_function


class RateLimiter:
    """Rate limiter with Redis backend support"""
    
    def __init__(self):
        self._store = {}
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            self.use_redis = True
        except Exception:
            self.use_redis = False
            self.redis = None
    
    def is_allowed(self, key: str, limit: int, window: int) -> tuple:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Rate limit key (e.g., IP + endpoint)
            limit: Maximum number of requests
            window: Time window in seconds
        
        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        now = time.time()
        
        if self.use_redis:
            try:
                pipe = self.redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, window)
                results = pipe.execute()
                count = results[0]
                
                remaining = max(0, limit - count)
                reset_time = int(now + window)
                
                return count <= limit, remaining, reset_time
            except Exception:
                pass
        
        # Fallback to in-memory store
        if key not in self._store:
            self._store[key] = {'count': 0, 'reset_time': now + window}
        
        bucket = self._store[key]
        
        # Reset if window has passed
        if now > bucket['reset_time']:
            bucket['count'] = 0
            bucket['reset_time'] = now + window
        
        bucket['count'] += 1
        remaining = max(0, limit - bucket['count'])
        
        return bucket['count'] <= limit, remaining, int(bucket['reset_time'])
    
    def get_client_identifier(self, request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get real IP behind proxy
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            ip = forwarded.split(',')[0].strip()
        else:
            ip = request.remote_addr or 'unknown'
        
        # Include user ID if authenticated
        user_id = getattr(g, 'user', {}).get('id')
        if user_id:
            return f"user:{user_id}"
        
        return f"ip:{ip}"


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit: int = 60, window: int = 60, key_func=None):
    """
    Rate limiting decorator
    
    Args:
        limit: Maximum number of requests in the window
        window: Time window in seconds
        key_func: Optional function to generate rate limit key
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(request)
            else:
                key = rate_limiter.get_client_identifier(request)
            
            # Include endpoint in key
            key = f"rate_limit:{key}:{request.endpoint}"
            
            # Check rate limit
            allowed, remaining, reset_time = rate_limiter.is_allowed(key, limit, window)
            
            # Set rate limit headers
            g.rate_limit_headers = {
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
            
            if not allowed:
                response = jsonify({
                    'code': 429,
                    'message': 'Rate limit exceeded. Please try again later.',
                    'data': {
                        'limit': limit,
                        'window': window,
                        'retry_after': reset_time - int(time.time())
                    }
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(reset_time - int(time.time()))
                return response
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def csrf_protect(f):
    """CSRF protection decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not security_middleware.check_csrf_token(request):
            logger.warning(f"CSRF token validation failed for {request.path}")
            return jsonify({
                'code': 403,
                'message': 'CSRF token validation failed',
                'data': None
            }), 403
        return f(*args, **kwargs)
    return decorated_function


def sanitize_output(data: Any, max_depth: int = 10, current_depth: int = 0) -> Any:
    """
    Recursively sanitize output data to prevent XSS in responses
    
    Args:
        data: Data to sanitize
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth
    """
    if current_depth > max_depth:
        return data
    
    if isinstance(data, dict):
        return {
            key: sanitize_output(value, max_depth, current_depth + 1)
            for key, value in data.items()
        }
    
    elif isinstance(data, list):
        return [
            sanitize_output(item, max_depth, current_depth + 1)
            for item in data
        ]
    
    elif isinstance(data, str):
        # Sanitize string output
        return security_middleware.sanitize_input(data)
    
    return data


def require_https(f):
    """Require HTTPS for the endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
            if current_app.config.get('APP_ENV') == 'production':
                return jsonify({
                    'code': 403,
                    'message': 'HTTPS required',
                    'data': None
                }), 403
        return f(*args, **kwargs)
    return decorated_function


def add_rate_limit_headers(response):
    """Add rate limit headers to response"""
    headers = getattr(g, 'rate_limit_headers', {})
    for key, value in headers.items():
        response.headers[key] = value
    return response
