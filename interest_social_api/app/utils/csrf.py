import os
import secrets
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request

class CSRFProtection:
    """CSRF防护中间件
    对于API服务，使用双重提交Cookie模式保护
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化CSRF防护"""
        self._app = app
        
        @app.before_request
        def csrf_protect():
            """请求前检查CSRF令牌"""
            if self._is_exempt(request.endpoint):
                return
            
            # 仅对修改状态的请求方法进行CSRF检查
            if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
                # 跳过GET, HEAD, OPTIONS, TRACE等安全方法
                if not self._verify_csrf_token():
                    return jsonify({
                        "code": 403,
                        "message": "CSRF令牌验证失败",
                        "data": None
                    }), 403
    
    def _verify_csrf_token(self):
        """验证CSRF令牌
        双重提交Cookie模式: 比较Cookie中的CSRF令牌和请求头中的CSRF令牌
        """
        # 从Cookie获取CSRF令牌
        csrf_cookie = request.cookies.get('XSRF-TOKEN')
        
        # 从请求头获取CSRF令牌
        csrf_header = request.headers.get('X-XSRF-TOKEN')
        
        # 如果没有CSRF令牌，尝试从请求数据中获取
        if not csrf_header:
            csrf_header = request.form.get('_csrf_token')
        
        if not csrf_cookie or not csrf_header:
            return False
        
        # 使用安全的字符串比较防止时序攻击
        return secrets.compare_digest(csrf_cookie, csrf_header)
    
    def _is_exempt(self, endpoint):
        """检查端点是否豁免CSRF检查"""
        if not endpoint:
            return False
        
        # 豁免的端点列表
        exempt_endpoints = [
            'auth.login',
            'auth.register',
            'auth.refresh',
            'static'
        ]
        
        return endpoint in exempt_endpoints

def generate_csrf_token():
    """生成CSRF令牌"""
    return secrets.token_urlsafe(32)

def csrf_protect(f):
    """CSRF保护装饰器（用于特定路由）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 跳过不需要CSRF保护的方法
        if request.method not in ('POST', 'PUT', 'DELETE', 'PATCH'):
            return f(*args, **kwargs)
        
        csrf_cookie = request.cookies.get('XSRF-TOKEN')
        csrf_header = request.headers.get('X-XSRF-TOKEN')
        
        if not csrf_cookie or not csrf_header:
            return jsonify({
                "code": 403,
                "message": "CSRF令牌验证失败",
                "data": None
            }), 403
        
        if not secrets.compare_digest(csrf_cookie, csrf_header):
            return jsonify({
                "code": 403,
                "message": "CSRF令牌验证失败",
                "data": None
            }), 403
        
        return f(*args, **kwargs)
    return decorated

# 用于JWT认证的CSRF保护
def jwt_csrf_protect(f):
    """JWT和CSRF双重保护装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 首先验证JWT
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({
                "code": 401,
                "message": "无效或缺失的认证令牌",
                "data": None
            }), 401
        
        # 然后验证CSRF
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            csrf_cookie = request.cookies.get('XSRF-TOKEN')
            csrf_header = request.headers.get('X-XSRF-TOKEN')
            
            if not csrf_cookie or not csrf_header:
                return jsonify({
                    "code": 403,
                    "message": "CSRF令牌验证失败",
                    "data": None
                }), 403
            
            if not secrets.compare_digest(csrf_cookie, csrf_header):
                return jsonify({
                    "code": 403,
                    "message": "CSRF令牌验证失败",
                    "data": None
                }), 403
        
        return f(*args, **kwargs)
    return decorated