from flask import Flask, Response
from config import Config
from app.routes import home, profile, message, news, system
from app.models.database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        init_default_data()
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    from app.routes.auth import auth_bp
    from app.routes.post import post_bp
    from app.routes.social import social_bp
    from app.routes.search import search_bp
    
    app.register_blueprint(home.home_bp)
    app.register_blueprint(profile.profile_bp)
    app.register_blueprint(message.message_bp)
    app.register_blueprint(news.news_bp)
    app.register_blueprint(system.system_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(search_bp)
    
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
                    "/api/system/check-update - 检查更新",
                    "/api/auth/register - 用户注册",
                    "/api/auth/login - 用户登录",
                    "/api/auth/logout - 用户登出",
                    "/api/auth/verify - Token验证",
                    "/api/posts - 帖子列表",
                    "/api/posts - 发布帖子",
                    "/api/posts/<post_id> - 帖子详情",
                    "/api/posts/<post_id> - 删除帖子",
                    "/api/posts/<post_id>/like - 点赞/取消点赞",
                    "/api/posts/<post_id>/comments - 评论列表",
                    "/api/posts/<post_id>/comments - 发表评论",
                    "/api/upload - 图片上传",
                    "/api/social/follow/<user_id> - 关注用户",
                    "/api/social/unfollow/<user_id> - 取消关注",
                    "/api/social/blacklist - 黑名单列表",
                    "/api/social/blacklist/<user_id> - 添加/移除黑名单",
                    "/api/search/users - 搜索用户",
                    "/api/search/posts - 搜索帖子",
                    "/api/search/topics - 搜索话题"
                ]
            }
        }
    
    return app

def init_default_data():
    from app.models.database import User, Topic
    
    if User.query.count() == 0:
        from werkzeug.security import generate_password_hash
        default_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            nickname='管理员',
            bio='系统管理员',
            is_verified=True,
            verified_type='官方认证'
        )
        db.session.add(default_user)
        db.session.commit()
    
    if Topic.query.count() == 0:
        topics = [
            Topic(name='#摄影技巧#', posts_count=12580, trend='up'),
            Topic(name='#旅行日记#', posts_count=9870, trend='up'),
            Topic(name='#美食分享#', posts_count=8650, trend='stable'),
            Topic(name='#户外运动#', posts_count=7230, trend='up'),
            Topic(name='#读书笔记#', posts_count=5120, trend='down')
        ]
        for topic in topics:
            db.session.add(topic)
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
