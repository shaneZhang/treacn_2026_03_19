from flask import Flask, request, jsonify
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.routes import home, profile, message, news, system, auth
from app.utils.security import init_security_headers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 配置CORS
    CORS(app, 
         origins=Config.CORS_ORIGINS,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-API-Key'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # 添加安全头
    init_security_headers(app)
    
    # 注册蓝图
    app.register_blueprint(auth.auth_bp, url_prefix='/api/auth')
    app.register_blueprint(home.home_bp, url_prefix='/api')
    app.register_blueprint(profile.profile_bp, url_prefix='/api')
    app.register_blueprint(message.message_bp, url_prefix='/api')
    app.register_blueprint(news.news_bp, url_prefix='/api')
    app.register_blueprint(system.system_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return jsonify({
            "code": 200,
            "message": "Welcome to Interest Social API",
            "data": {
                "endpoints": [
                    "/api/auth/login - 用户登录",
                    "/api/auth/refresh - 刷新Token",
                    "/api/auth/logout - 用户登出",
                    "/api/home - 首页数据（需要认证）",
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
                    "/api/system/check-update - 检查更新"
                ]
            }
        })
    
    # JWT错误处理
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({
            "code": 401,
            "message": "缺少认证Token",
            "data": None
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({
            "code": 401,
            "message": "无效的Token",
            "data": None
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "code": 401,
            "message": "Token已过期",
            "data": None
        }), 401
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
