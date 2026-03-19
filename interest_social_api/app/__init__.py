from flask import Flask, Response
from config import Config
from app.routes import home, profile, message, news, system

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    app.register_blueprint(home.home_bp)
    app.register_blueprint(profile.profile_bp)
    app.register_blueprint(message.message_bp)
    app.register_blueprint(news.news_bp)
    app.register_blueprint(system.system_bp)
    
    @app.route('/')
    def index():
        return {
            "code": 200,
            "message": "Welcome to Interest Social API",
            "data": {
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
                    "/api/system/check-update - 检查更新"
                ]
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
