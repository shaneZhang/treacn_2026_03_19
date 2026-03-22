import re
import bleach
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os
import html

# 初始化加密工具
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key().decode())
if isinstance(ENCRYPTION_KEY, str):
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
fernet = Fernet(ENCRYPTION_KEY)

# SQL注入检测正则模式
SQL_INJECTION_PATTERNS = [
    r'(\%27)|(\')|(\-\-)|(\%23)|(#)',
    r'((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))',
    r'(\%27)|(\')|(\-\-)|(\%23)|(#)',
    r'union.*select',
    r'insert.*into',
    r'delete.*from',
    r'drop.*table',
    r'update.*set',
    r'alter.*table',
    r'exec.*',
    r'script',
    r'iframe',
]

# XSS清理配置
BLEACH_ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
    'em', 'i', 'li', 'ol', 'strong', 'ul', 'p', 'br', 'span'
]
BLEACH_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'abbr': ['title'],
    'acronym': ['title'],
}

def init_security_headers(app):
    """初始化安全头"""
    @app.after_request
    def add_security_headers(response):
        # 防止点击劫持
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # XSS防护
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # 防止MIME类型嗅探
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # 内容安全策略
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        # 引用策略
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # 隐藏服务器信息
        response.headers['Server'] = 'Protected'
        # HSTS（生产环境启用HTTPS后使用
        if os.getenv('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

def sanitize_input(input_string):
    """清理用户输入，防止XSS"""
    if not input_string:
        return input_string
    
    # 转义HTML特殊字符
    sanitized = html.escape(input_string)
    
    # 使用bleach进一步清理
    sanitized = bleach.clean(
        sanitized,
        tags=BLEACH_ALLOWED_TAGS,
        attributes=BLEACH_ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return sanitized

def sanitize_dict(data_dict):
    """递归清理字典中的字符串"""
    if isinstance(data_dict, dict):
        return {k: sanitize_dict(v) for k, v in data_dict.items()}
    elif isinstance(data_dict, list):
        return [sanitize_dict(item) for item in data_dict]
    elif isinstance(data_dict, str):
        return sanitize_input(data_dict)
    else:
        return data_dict

def detect_sql_injection(input_string):
    """检测SQL注入"""
    if not input_string or not isinstance(input_string, str):
        return False
    
    input_lower = input_string.lower()
    
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, input_lower, re.IGNORECASE):
            return True
    
    return False

def validate_input(input_data):
    """验证用户输入"""
    if isinstance(input_data, str):
        if detect_sql_injection(input_data):
            return False, "检测到潜在的恶意输入"
        return True, None
    
    elif isinstance(input_data, dict):
        for key, value in input_data.items():
            if isinstance(value, str) and detect_sql_injection(value):
                return False, f"检测到潜在的恶意输入在字段: {key}"
            elif isinstance(value, (dict, list)):
                result, msg = validate_input(value)
                if not result:
                    return False, msg
    
    elif isinstance(input_data, list):
        for item in input_data:
            result, msg = validate_input(item)
            if not result:
                return False, msg
    
    return True, None

def input_validation(f):
    """输入验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 检查查询参数
        if request.args:
            for key, value in request.args.items():
                if detect_sql_injection(value):
                    return jsonify({
                        "code": 400,
                        "message": f"检测到潜在的恶意输入在参数: {key}",
                        "data": None
                    }), 400
        
        # 检查JSON数据
        if request.is_json:
            data = request.get_json()
            is_valid, message = validate_input(data)
            if not is_valid:
                return jsonify({
                    "code": 400,
                    "message": message,
                    "data": None
                }), 400
        
        return f(*args, **kwargs)
    return decorated

# 密码哈希函数
def hash_password(password):
    """哈希密码"""
    return generate_password_hash(password, method='pbkdf2:sha256:600000', salt_length=16)

def verify_password(password_hash, password):
    """验证密码"""
    return check_password_hash(password_hash, password)

# 敏感数据加密函数
def encrypt_sensitive_data(data):
    """加密敏感数据"""
    if not data:
        return None
    if isinstance(data, str):
        data = data.encode()
    return fernet.encrypt(data).decode()

def decrypt_sensitive_data(encrypted_data):
    """解密敏感数据"""
    if not encrypted_data:
        return None
    if isinstance(encrypted_data, str):
        encrypted_data = encrypted_data.encode()
    try:
        return fernet.decrypt(encrypted_data).decode()
    except:
        return None

# API密钥验证
def verify_api_key(api_key):
    """验证API密钥"""
    valid_api_key = os.getenv('API_KEY')
    if not valid_api_key:
        return False
    return api_key == valid_api_key

def api_key_required(f):
    """API密钥验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not verify_api_key(api_key):
            return jsonify({
                "code": 401,
                "message": "无效或缺失的API密钥",
                "data": None
            }), 401
        return f(*args, **kwargs)
    return decorated