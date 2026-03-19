import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs'))

from flask import Flask, Response
from config import Config
from app.routes import home, profile, message, news, system, auth, posts, social, search
from app.models import db
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Register blueprints
    app.register_blueprint(home.home_bp)
    app.register_blueprint(profile.profile_bp)
    app.register_blueprint(message.message_bp)
    app.register_blueprint(news.news_bp)
    app.register_blueprint(system.system_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(posts.posts_bp)
    app.register_blueprint(social.social_bp)
    app.register_blueprint(search.search_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Serve uploaded files
    from flask import send_from_directory
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/')
    def index():
        return {
            "code": 200,
            "message": "Welcome to Interest Social API",
            "data": {
                "endpoints": [
                    # Auth endpoints
                    "/api/auth/register - 用户注册",
                    "/api/auth/login - 用户登录",
                    "/api/auth/refresh - 刷新Token",
                    "/api/auth/logout - 用户登出",
                    "/api/auth/me - 获取当前用户信息",
                    "/api/auth/change-password - 修改密码",
                    
                    # Post endpoints
                    "/api/posts - 获取帖子列表/发布帖子",
                    "/api/posts/<post_id> - 获取/删除帖子详情",
                    "/api/posts/<post_id>/like - 点赞/取消点赞",
                    "/api/posts/<post_id>/comments - 获取/发布评论",
                    "/api/posts/upload-image - 上传图片",
                    
                    # Social endpoints
                    "/api/social/follow/<user_id> - 关注用户",
                    "/api/social/unfollow/<user_id> - 取消关注",
                    "/api/social/block/<user_id> - 拉黑用户",
                    "/api/social/unblock/<user_id> - 取消拉黑",
                    "/api/social/blocklist - 黑名单列表",
                    
                    # Search endpoints
                    "/api/search/users - 搜索用户",
                    "/api/search/posts - 搜索帖子",
                    "/api/search/topics - 搜索话题",
                    
                    # Existing endpoints
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
