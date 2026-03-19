from flask import Blueprint, jsonify, request

from app.models.database import db, User, Post, Topic, Follow, Blacklist
from app.routes.auth import token_required

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('/users', methods=['GET'])
def search_users():
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    if not keyword:
        return jsonify({
            'code': 400,
            'message': '搜索关键词不能为空',
            'data': None
        }), 400
    
    query = User.query.filter(
        db.or_(
            User.username.like(f'%{keyword}%'),
            User.nickname.like(f'%{keyword}%'),
            User.bio.like(f'%{keyword}%')
        )
    ).filter_by(is_active=True)
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    users = []
    for user in pagination.items:
        user_data = user.to_dict()
        user_data['followers_count'] = Follow.query.filter_by(following_id=user.id).count()
        users.append(user_data)
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'users': users,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next,
            'keyword': keyword
        }
    })

@search_bp.route('/posts', methods=['GET'])
def search_posts():
    keyword = request.args.get('keyword', '').strip()
    topic = request.args.get('topic', '').strip()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    if not keyword and not topic:
        return jsonify({
            'code': 400,
            'message': '搜索关键词或话题不能为空',
            'data': None
        }), 400
    
    query = Post.query.filter_by(is_deleted=False)
    
    if keyword:
        query = query.filter(Post.content.like(f'%{keyword}%'))
    
    if topic:
        query = query.filter(Post.topic.like(f'%{topic}%'))
    
    query = query.order_by(Post.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    posts = [post.to_dict() for post in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'posts': posts,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next,
            'keyword': keyword,
            'topic': topic
        }
    })

@search_bp.route('/topics', methods=['GET'])
def search_topics():
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    if not keyword:
        query = Topic.query.order_by(Topic.posts_count.desc())
    else:
        query = Topic.query.filter(
            db.or_(
                Topic.name.like(f'%{keyword}%'),
                Topic.description.like(f'%{keyword}%')
            )
        ).order_by(Topic.posts_count.desc())
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    topics = [topic.to_dict() for topic in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'topics': topics,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next,
            'keyword': keyword
        }
    })

@search_bp.route('/all', methods=['GET'])
def search_all():
    keyword = request.args.get('keyword', '').strip()
    
    if not keyword:
        return jsonify({
            'code': 400,
            'message': '搜索关键词不能为空',
            'data': None
        }), 400
    
    users = User.query.filter(
        db.or_(
            User.username.like(f'%{keyword}%'),
            User.nickname.like(f'%{keyword}%')
        )
    ).filter_by(is_active=True).limit(5).all()
    
    posts = Post.query.filter(
        Post.content.like(f'%{keyword}%')
    ).filter_by(is_deleted=False).order_by(Post.created_at.desc()).limit(5).all()
    
    topics = Topic.query.filter(
        Topic.name.like(f'%{keyword}%')
    ).order_by(Topic.posts_count.desc()).limit(5).all()
    
    users_data = []
    for user in users:
        user_data = user.to_dict()
        user_data['followers_count'] = Follow.query.filter_by(following_id=user.id).count()
        users_data.append(user_data)
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'users': users_data,
            'posts': [post.to_dict() for post in posts],
            'topics': [topic.to_dict() for topic in topics],
            'keyword': keyword
        }
    })

@search_bp.route('/hot-topics', methods=['GET'])
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

@search_bp.route('/suggest', methods=['GET'])
def get_suggestions():
    keyword = request.args.get('keyword', '').strip()
    limit = request.args.get('limit', 10, type=int)
    
    if not keyword or len(keyword) < 2:
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'suggestions': []
            }
        })
    
    users = User.query.filter(
        db.or_(
            User.username.like(f'{keyword}%'),
            User.nickname.like(f'{keyword}%')
        )
    ).filter_by(is_active=True).limit(limit).all()
    
    topics = Topic.query.filter(
        Topic.name.like(f'%{keyword}%')
    ).limit(limit).all()
    
    suggestions = []
    
    for user in users:
        suggestions.append({
            'type': 'user',
            'id': user.id,
            'name': user.nickname,
            'avatar': user.avatar,
            'subtitle': f'@{user.username}'
        })
    
    for topic in topics:
        suggestions.append({
            'type': 'topic',
            'id': topic.id,
            'name': topic.name,
            'subtitle': f'{topic.posts_count} 帖子'
        })
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'suggestions': suggestions[:limit]
        }
    })

@search_bp.route('/history', methods=['GET'])
@token_required
def get_search_history(current_user):
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'history': []
        }
    })

@search_bp.route('/history', methods=['DELETE'])
@token_required
def clear_search_history(current_user):
    return jsonify({
        'code': 200,
        'message': '搜索历史已清除',
        'data': None
    })
