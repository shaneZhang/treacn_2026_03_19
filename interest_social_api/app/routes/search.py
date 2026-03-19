from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Post, Topic
from sqlalchemy import or_

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search/users', methods=['GET'])
def search_users():
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    if not keyword:
        return jsonify({
            "code": 400,
            "message": "请输入搜索关键词"
        }), 400
    
    # Search by username, nickname, or bio
    users = User.query.filter(
        or_(
            User.username.like(f'%{keyword}%'),
            User.nickname.like(f'%{keyword}%'),
            User.bio.like(f'%{keyword}%')
        )
    ).paginate(page=page, per_page=page_size, error_out=False)
    
    # Check follow status for current user
    current_user = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        if current_user_id:
            current_user = User.query.get(int(current_user_id))
    except:
        pass
    
    user_list = []
    for user in users.items:
        user_dict = user.to_dict()
        if current_user and current_user.id != user.id:
            user_dict['is_following'] = current_user.is_following(user)
        else:
            user_dict['is_following'] = False
        user_list.append(user_dict)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "users": user_list,
            "total": users.total,
            "page": page,
            "page_size": page_size,
            "has_more": users.has_next
        }
    })

@search_bp.route('/api/search/posts', methods=['GET'])
def search_posts():
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    topic = request.args.get('topic')
    
    if not keyword and not topic:
        return jsonify({
            "code": 400,
            "message": "请输入搜索关键词或话题"
        }), 400
    
    query = Post.query.filter_by(is_public=True)
    
    # Search by keyword in content
    if keyword:
        query = query.filter(Post.content.like(f'%{keyword}%'))
    
    # Search by topic
    if topic:
        query = query.filter(Post.topic.like(f'%{topic}%'))
    
    # Filter by user
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    posts = query.order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=page_size, error_out=False)
    
    # Get current user if authenticated
    current_user = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        if current_user_id:
            current_user = User.query.get(int(current_user_id))
    except:
        pass
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "posts": [post.to_dict(current_user) for post in posts.items],
            "total": posts.total,
            "page": page,
            "page_size": page_size,
            "has_more": posts.has_next
        }
    })

@search_bp.route('/api/search/topics', methods=['GET'])
def search_topics():
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    if not keyword:
        return jsonify({
            "code": 400,
            "message": "请输入搜索关键词"
        }), 400
    
    # Search by topic name
    topics = Topic.query.filter(
        Topic.name.like(f'%{keyword}%')
    ).order_by(Topic.posts_count.desc())\
     .paginate(page=page, per_page=page_size, error_out=False)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "topics": [topic.to_dict() for topic in topics.items],
            "total": topics.total,
            "page": page,
            "page_size": page_size,
            "has_more": topics.has_next
        }
    })

@search_bp.route('/api/search/hot-topics', methods=['GET'])
def get_hot_topics():
    limit = request.args.get('limit', 10, type=int)
    if limit > 50:
        limit = 50
    
    # Get topics sorted by post count
    topics = Topic.query.order_by(Topic.posts_count.desc()).limit(limit).all()
    
    # If no topics exist, return default hot topics
    if not topics:
        default_topics = [
            {"id": 1, "name": "#摄影技巧#", "posts_count": 12580, "trend": "up"},
            {"id": 2, "name": "#旅行日记#", "posts_count": 9870, "trend": "up"},
            {"id": 3, "name": "#美食分享#", "posts_count": 8650, "trend": "stable"},
            {"id": 4, "name": "#户外运动#", "posts_count": 7230, "trend": "up"},
            {"id": 5, "name": "#读书笔记#", "posts_count": 5120, "trend": "down"},
            {"id": 6, "name": "#健身打卡#", "posts_count": 4890, "trend": "up"},
            {"id": 7, "name": "#音乐分享#", "posts_count": 4230, "trend": "stable"},
            {"id": 8, "name": "#电影推荐#", "posts_count": 3890, "trend": "up"}
        ]
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "topics": default_topics[:limit]
            }
        })
    
    topic_list = []
    for i, topic in enumerate(topics):
        topic_dict = topic.to_dict()
        # Add trend indicator (simplified)
        if i < len(topics) // 3:
            topic_dict['trend'] = 'up'
        elif i < 2 * len(topics) // 3:
            topic_dict['trend'] = 'stable'
        else:
            topic_dict['trend'] = 'down'
        topic_list.append(topic_dict)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "topics": topic_list
        }
    })

@search_bp.route('/api/search/suggestions', methods=['GET'])
def get_search_suggestions():
    keyword = request.args.get('keyword', '').strip()
    limit = request.args.get('limit', 5, type=int)
    
    if not keyword:
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "suggestions": []
            }
        })
    
    suggestions = []
    
    # Search users
    users = User.query.filter(
        or_(
            User.username.like(f'%{keyword}%'),
            User.nickname.like(f'%{keyword}%')
        )
    ).limit(limit).all()
    
    for user in users:
        suggestions.append({
            "type": "user",
            "id": user.id,
            "text": user.nickname or user.username,
            "avatar": user.avatar
        })
    
    # Search topics
    topics = Topic.query.filter(
        Topic.name.like(f'%{keyword}%')
    ).limit(limit).all()
    
    for topic in topics:
        suggestions.append({
            "type": "topic",
            "id": topic.id,
            "text": topic.name,
            "posts_count": topic.posts_count
        })
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "suggestions": suggestions
        }
    })
