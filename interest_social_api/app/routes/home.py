from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Post, Topic

home_bp = Blueprint('home', __name__)

# Static banners data (can be moved to database later)
home_banners = [
    {
        "id": 1,
        "title": "春季摄影大赛火热进行中",
        "image": "https://picsum.photos/750/300?random=1",
        "link": "https://example.com/event/1",
        "link_type": "event"
    },
    {
        "id": 2,
        "title": "新功能上线：兴趣圈子等你来",
        "image": "https://picsum.photos/750/300?random=2",
        "link": "https://example.com/circle",
        "link_type": "h5"
    },
    {
        "id": 3,
        "title": "周末户外活动招募中",
        "image": "https://picsum.photos/750/300?random=3",
        "link": "https://example.com/activity/2",
        "link_type": "activity"
    }
]

interest_categories = [
    {"id": 1, "name": "摄影", "icon": "camera", "posts_count": 25680},
    {"id": 2, "name": "旅行", "icon": "plane", "posts_count": 18920},
    {"id": 3, "name": "美食", "icon": "food", "posts_count": 15430},
    {"id": 4, "name": "运动", "icon": "sport", "posts_count": 12350},
    {"id": 5, "name": "阅读", "icon": "book", "posts_count": 9870},
    {"id": 6, "name": "音乐", "icon": "music", "posts_count": 8650},
    {"id": 7, "name": "绘画", "icon": "art", "posts_count": 6540},
    {"id": 8, "name": "游戏", "icon": "game", "posts_count": 12300}
]

@home_bp.route('/api/home', methods=['GET'])
@jwt_required(optional=True)
def get_home_data():
    current_user_id = get_jwt_identity()
    current_user_obj = None
    if current_user_id:
        current_user_obj = User.query.get(int(current_user_id))
    
    # Get hot topics from database
    hot_topics = Topic.query.order_by(Topic.posts_count.desc()).limit(5).all()
    if not hot_topics:
        hot_topics = [
            {"id": 1, "name": "#摄影技巧#", "posts_count": 12580, "trend": "up"},
            {"id": 2, "name": "#旅行日记#", "posts_count": 9870, "trend": "up"},
            {"id": 3, "name": "#美食分享#", "posts_count": 8650, "trend": "stable"},
            {"id": 4, "name": "#户外运动#", "posts_count": 7230, "trend": "up"},
            {"id": 5, "name": "#读书笔记#", "posts_count": 5120, "trend": "down"}
        ]
    else:
        hot_topics = []
        for i, topic in enumerate(Topic.query.order_by(Topic.posts_count.desc()).limit(5).all()):
            topic_dict = topic.to_dict()
            if i < 2:
                topic_dict['trend'] = 'up'
            elif i < 4:
                topic_dict['trend'] = 'stable'
            else:
                topic_dict['trend'] = 'down'
            hot_topics.append(topic_dict)
    
    # Get recommended posts
    posts = Post.query.filter_by(is_public=True)\
        .order_by(Post.created_at.desc())\
        .limit(10)\
        .all()
    
    # Get recommended users (users with most posts)
    users = User.query.order_by(User.id.desc()).limit(6).all()
    recommended_users = []
    for user in users:
        if current_user_obj and current_user_obj.id != user.id:
            is_following = current_user_obj.is_following(user)
        else:
            is_following = False
        recommended_users.append({
            "id": user.id,
            "nickname": user.nickname or user.username,
            "avatar": user.avatar or f"https://picsum.photos/200/200?random={user.id}",
            "bio": user.bio or "",
            "is_following": is_following,
            "followers_count": user.followers_count
        })
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "banners": home_banners,
            "hot_topics": hot_topics,
            "recommended_users": recommended_users,
            "recommended_posts": [post.to_dict(current_user_obj) for post in posts],
            "interest_categories": interest_categories
        }
    })

