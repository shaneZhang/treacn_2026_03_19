from flask import Blueprint, request, jsonify
from app.models.database import db, User, Post, Topic, Follow
from app.routes.auth import token_required

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search/users', methods=['GET'])
def search_users():
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if not keyword:
        return jsonify({
            'code': 400,
            'message': '搜索关键词不能为空',
            'data': None
        }), 400
    
    query = User.query.filter(
        db.or_(
            User.nickname.contains(keyword),
            User.username.contains(keyword),
            User.bio.contains(keyword)
        )
    )
    
    pagination = query.order_by(User.followers_count.desc() if hasattr(User, 'followers_count') else User.id)\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    current_user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header:
        import jwt
        from flask import current_app
        try:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload.get('user_id')
        except:
            pass
    
    users = []
    for user in pagination.items:
        user_dict = user.to_simple_dict()
        user_dict['followers_count'] = user.followers.count()
        
        if current_user_id:
            is_following = Follow.query.filter_by(
                follower_id=current_user_id, 
                followed_id=user.id
            ).first() is not None
            user_dict['is_following'] = is_following
        else:
            user_dict['is_following'] = False
        
        users.append(user_dict)
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'users': users,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next,
            'keyword': keyword
        }
    })

@search_bp.route('/api/search/posts', methods=['GET'])
def search_posts():
    keyword = request.args.get('keyword', '').strip()
    topic = request.args.get('topic', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if not keyword and not topic:
        return jsonify({
            'code': 400,
            'message': '搜索关键词或话题不能为空',
            'data': None
        }), 400
    
    query = Post.query.filter_by(is_deleted=False)
    
    if keyword:
        query = query.filter(Post.content.contains(keyword))
    
    if topic:
        query = query.filter(Post.topic.contains(topic))
    
    pagination = query.order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    current_user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header:
        import jwt
        from flask import current_app
        try:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload.get('user_id')
        except:
            pass
    
    posts = [post.to_dict(current_user_id) for post in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'posts': posts,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next,
            'keyword': keyword,
            'topic': topic
        }
    })

@search_bp.route('/api/search/topics', methods=['GET'])
def search_topics():
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Topic.query
    
    if keyword:
        query = query.filter(Topic.name.contains(keyword))
    
    pagination = query.order_by(Topic.posts_count.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    topics = [topic.to_dict() for topic in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'topics': topics,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next,
            'keyword': keyword
        }
    })

@search_bp.route('/api/search/hot-topics', methods=['GET'])
def get_hot_topics():
    limit = request.args.get('limit', 10, type=int)
    
    topics = Topic.query.order_by(Topic.posts_count.desc()).limit(limit).all()
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'topics': [topic.to_dict() for topic in topics]
        }
    })

@search_bp.route('/api/search', methods=['GET'])
def global_search():
    keyword = request.args.get('keyword', '').strip()
    
    if not keyword:
        return jsonify({
            'code': 400,
            'message': '搜索关键词不能为空',
            'data': None
        }), 400
    
    users = User.query.filter(
        db.or_(
            User.nickname.contains(keyword),
            User.username.contains(keyword)
        )
    ).limit(5).all()
    
    posts = Post.query.filter(
        Post.content.contains(keyword),
        Post.is_deleted == False
    ).order_by(Post.created_at.desc()).limit(5).all()
    
    topics = Topic.query.filter(
        Topic.name.contains(keyword)
    ).limit(5).all()
    
    current_user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header:
        import jwt
        from flask import current_app
        try:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload.get('user_id')
        except:
            pass
    
    user_results = []
    for user in users:
        user_dict = user.to_simple_dict()
        user_dict['followers_count'] = user.followers.count()
        if current_user_id:
            is_following = Follow.query.filter_by(
                follower_id=current_user_id, 
                followed_id=user.id
            ).first() is not None
            user_dict['is_following'] = is_following
        user_results.append(user_dict)
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'keyword': keyword,
            'users': user_results,
            'posts': [post.to_dict(current_user_id) for post in posts],
            'topics': [topic.to_dict() for topic in topics]
        }
    })
