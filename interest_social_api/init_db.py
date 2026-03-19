import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.database import User, Post, Comment, Like, Follow, Blacklist, Topic, TokenBlacklist, Image
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")
        
        if User.query.count() == 0:
            print("正在初始化测试数据...")
            
            test_users = [
                {
                    'username': 'test_user1',
                    'password': '123456',
                    'nickname': '测试用户1',
                    'avatar': 'https://picsum.photos/200/200?random=1',
                    'bio': '这是测试用户1的简介',
                    'gender': 1,
                    'location': '北京'
                },
                {
                    'username': 'test_user2',
                    'password': '123456',
                    'nickname': '测试用户2',
                    'avatar': 'https://picsum.photos/200/200?random=2',
                    'bio': '这是测试用户2的简介',
                    'gender': 2,
                    'location': '上海'
                },
                {
                    'username': 'photographer',
                    'password': '123456',
                    'nickname': '摄影大师',
                    'avatar': 'https://picsum.photos/200/200?random=3',
                    'bio': '用镜头记录美好生活',
                    'gender': 1,
                    'location': '深圳',
                    'is_verified': True,
                    'verified_type': '兴趣达人'
                },
                {
                    'username': 'traveler',
                    'password': '123456',
                    'nickname': '旅行达人',
                    'avatar': 'https://picsum.photos/200/200?random=4',
                    'bio': '走遍世界每个角落',
                    'gender': 2,
                    'location': '广州',
                    'is_verified': True,
                    'verified_type': '旅行博主'
                }
            ]
            
            for user_data in test_users:
                password = user_data.pop('password')
                user = User(**user_data, password_hash=generate_password_hash(password))
                db.session.add(user)
            
            db.session.commit()
            print(f"创建了 {len(test_users)} 个测试用户")
            
            topics = [
                {'name': '#摄影技巧#', 'description': '分享摄影技巧和心得', 'posts_count': 12580},
                {'name': '#旅行日记#', 'description': '记录旅行中的美好瞬间', 'posts_count': 9870},
                {'name': '#美食分享#', 'description': '分享美食制作和探店体验', 'posts_count': 8650},
                {'name': '#户外运动#', 'description': '户外运动爱好者的聚集地', 'posts_count': 7230},
                {'name': '#读书笔记#', 'description': '分享读书心得和推荐', 'posts_count': 5120}
            ]
            
            for topic_data in topics:
                topic = Topic(**topic_data)
                db.session.add(topic)
            
            db.session.commit()
            print(f"创建了 {len(topics)} 个话题")
            
            print("测试数据初始化完成！")

if __name__ == '__main__':
    init_db()
