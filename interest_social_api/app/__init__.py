import logging
import os
from flask import Flask, Response, request, jsonify, g
from flask_cors import CORS
from config import Config, get_config
from app.routes import home, profile, message, news, system
from app.routes.auth import auth_bp
from app.middleware.security import add_security_headers, rate_limit, validate_input, rate_limiter

def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    cors_origins = config.CORS_ORIGINS if config.CORS_ORIGINS != ['*'] else '*'
    CORS(app, 
         origins=cors_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'X-API-Key'],
         expose_headers=['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'Retry-After'],
         max_age=3600,
         supports_credentials=True)
    
    add_security_headers(app)
    
    @app.before_request
    def before_request():
        g.request_start_time = None
        if not request.path.startswith('/health') and not request.path.startswith('/ready'):
            g.request_start_time = os.times()
    
    @app.after_request
    def after_request(response):
        if request.path.startswith('/health') or request.path.startswith('/ready'):
            return response
        
        if config.APP_ENV == 'production':
            if 'Server' in response.headers:
                del response.headers['Server']
            if 'X-Powered-By' in response.headers:
                del response.headers['X-Powered-By']
        
        response.headers['X-Request-ID'] = request.headers.get('X-Request-ID', os.urandom(8).hex())
        
        return response
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'code': 400,
            'message': 'Bad Request',
            'data': None
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'code': 401,
            'message': 'Unauthorized',
            'data': None
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'code': 403,
            'message': 'Forbidden',
            'data': None
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'message': 'Not Found',
            'data': None
        }), 404
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            'code': 429,
            'message': 'Too Many Requests',
            'data': None
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal Server Error: {str(error)}')
        return jsonify({
            'code': 500,
            'message': 'Internal Server Error',
            'data': None
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.exception(f'Unhandled exception: {str(error)}')
        return jsonify({
            'code': 500,
            'message': 'Internal Server Error' if config.APP_ENV == 'production' else str(error),
            'data': None
        }), 500
    
    app.register_blueprint(home.home_bp)
    app.register_blueprint(profile.profile_bp)
    app.register_blueprint(message.message_bp)
    app.register_blueprint(news.news_bp)
    app.register_blueprint(system.system_bp)
    app.register_blueprint(auth_bp)
    
    @app.route('/')
    @rate_limit(limit=100, window=60)
    def index():
        return {
            "code": 200,
            "message": "Welcome to Interest Social API",
            "data": {
                "version": os.environ.get('APP_VERSION', '1.0.0'),
                "endpoints": [
                    "/api/home - 首页数据",
                    "/api/profile - 我的（用户中心）",
                    "/api/profile/posts - 用户帖子",
                    "/api/profile/followers - 粉丝列表",
                    "/api/profile/following - 关注列表",
                    "/api/profile/liked - 点赞列表",
                    "/api/messages/notifications - 通知列表",
                    "/api/messages/conversations - 会话列表",
                    "/api/messages/private/<user_id> - 私信详情",
                    "/api/messages/send - 发送私信",
                    "/api/messages/check-read/<user_id> - 检查已读",
                    "/api/news - 新闻列表",
                    "/api/news/<news_id> - 新闻详情",
                    "/api/system/check-update - 检查更新",
                    "/api/auth/register - 用户注册",
                    "/api/auth/login - 用户登录",
                    "/api/auth/refresh - 刷新Token",
                    "/api/auth/logout - 用户登出",
                    "/api/auth/me - 当前用户信息",
                    "/api/auth/api-keys - 创建API密钥"
                ]
            }
        }
    
    logger.info(f"Interest Social API initialized in {config.APP_ENV} mode")
    
    return app
