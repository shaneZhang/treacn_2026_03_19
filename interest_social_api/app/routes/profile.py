from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Post, Like, Follow

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
@profile_bp.route('/api/profile/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
def get_profile(user_id=None):
    current_user_id = get_jwt_identity()
    
    # If no user_id provided, use current user
    if user_id is None:
        if not current_user_id:
            return jsonify({
                "code": 401,
                "message": "请先登录"
            }), 401
        user_id = current_user_id
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    # Check follow status
    is_following = False
    is_blocked = False
    if current_user_id and current_user_id != user_id:
        current_user = User.query.get(int(current_user_id))
        if current_user:
            is_following = current_user.is_following(user)
            is_blocked = user.is_blocking(current_user)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "user": user.to_dict(),
            "is_following": is_following,
            "is_blocked": is_blocked,
            "is_owner": int(current_user_id) == user_id,
            "stats": {
                "posts_count": user.posts_count,
                "followers_count": user.followers_count,
                "following_count": user.following_count,
                "likes_count": user.likes_count
            }
        }
    })

@profile_bp.route('/api/profile/posts', methods=['GET'])
@profile_bp.route('/api/profile/<int:user_id>/posts', methods=['GET'])
@jwt_required(optional=True)
def get_user_posts(user_id=None):
    current_user_id = get_jwt_identity()
    
    if user_id is None:
        if not current_user_id:
            return jsonify({
                "code": 401,
                "message": "请先登录"
            }), 401
        user_id = current_user_id
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    # Check if current user can view private posts
    current_user_obj = None
    if current_user_id:
        current_user_obj = User.query.get(int(current_user_id))
    
    query = Post.query.filter_by(user_id=user_id)
    if current_user_id != user_id:
        query = query.filter_by(is_public=True)
    
    posts = query.order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=page_size, error_out=False)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "posts": [post.to_dict(current_user_obj) for post in posts.items],
            "total": posts.total,
            "page": page,
            "page_size": page_size,
            "has_more": posts.has_next
        }
    })

@profile_bp.route('/api/profile/followers', methods=['GET'])
@profile_bp.route('/api/profile/<int:user_id>/followers', methods=['GET'])
@jwt_required(optional=True)
def get_followers(user_id=None):
    current_user_id = get_jwt_identity()
    
    if user_id is None:
        if not current_user_id:
            return jsonify({
                "code": 401,
                "message": "请先登录"
            }), 401
        user_id = current_user_id
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    followers = Follow.query.filter_by(followed_id=user_id)\
        .order_by(Follow.created_at.desc())\
        .paginate(page=page, per_page=page_size, error_out=False)
    
    current_user_obj = None
    if current_user_id:
        current_user_obj = User.query.get(int(current_user_id))
    
    follower_list = []
    for follow in followers.items:
        follower = User.query.get(follow.follower_id)
        if follower:
            follower_dict = follower.to_dict()
            follower_dict['followed_at'] = follow.created_at.isoformat() + 'Z'
            if current_user_obj and current_user_obj.id != follower.id:
                follower_dict['is_following'] = current_user_obj.is_following(follower)
            else:
                follower_dict['is_following'] = False
            follower_list.append(follower_dict)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "followers": follower_list,
            "total": followers.total,
            "page": page,
            "page_size": page_size,
            "has_more": followers.has_next
        }
    })

@profile_bp.route('/api/profile/following', methods=['GET'])
@profile_bp.route('/api/profile/<int:user_id>/following', methods=['GET'])
@jwt_required(optional=True)
def get_following(user_id=None):
    current_user_id = get_jwt_identity()
    
    if user_id is None:
        if not current_user_id:
            return jsonify({
                "code": 401,
                "message": "请先登录"
            }), 401
        user_id = current_user_id
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    following = Follow.query.filter_by(follower_id=user_id)\
        .order_by(Follow.created_at.desc())\
        .paginate(page=page, per_page=page_size, error_out=False)
    
    current_user_obj = None
    if current_user_id:
        current_user_obj = User.query.get(int(current_user_id))
    
    following_list = []
    for follow in following.items:
        followed_user = User.query.get(follow.followed_id)
        if followed_user:
            user_dict = followed_user.to_dict()
            user_dict['followed_at'] = follow.created_at.isoformat() + 'Z'
            if current_user_obj and current_user_obj.id != user_id:
                user_dict['is_following'] = current_user_obj.is_following(followed_user)
            else:
                user_dict['is_following'] = True
            following_list.append(user_dict)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "following": following_list,
            "total": following.total,
            "page": page,
            "page_size": page_size,
            "has_more": following.has_next
        }
    })

@profile_bp.route('/api/profile/liked', methods=['GET'])
@jwt_required()
def get_liked_posts():
    current_user_id = get_jwt_identity()
    current_user_obj = User.query.get(int(current_user_id))
    
    if not current_user_obj:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    # Get liked posts
    liked_posts = Post.query.join(Like)\
        .filter(Like.user_id == current_user_id)\
        .filter(Post.is_public == True)\
        .order_by(Like.created_at.desc())\
        .paginate(page=page, per_page=page_size, error_out=False)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "posts": [post.to_dict(current_user_obj) for post in liked_posts.items],
            "total": liked_posts.total,
            "page": page,
            "page_size": page_size,
            "has_more": liked_posts.has_next
        }
    })

