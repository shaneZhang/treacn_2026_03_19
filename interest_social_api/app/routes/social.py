from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Follow, Blacklist
from datetime import datetime

social_bp = Blueprint('social', __name__)

@social_bp.route('/api/social/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user_id = get_jwt_identity()
    
    if int(current_user_id) == user_id:
        return jsonify({
            "code": 400,
            "message": "不能关注自己"
        }), 400
    
    current_user = User.query.get(int(current_user_id))
    user_to_follow = User.query.get(user_id)
    
    if not current_user:
        return jsonify({
            "code": 404,
            "message": "当前用户不存在"
        }), 404
    
    if not user_to_follow:
        return jsonify({
            "code": 404,
            "message": "要关注的用户不存在"
        }), 404
    
    if current_user.is_following(user_to_follow):
        return jsonify({
            "code": 400,
            "message": "已经关注了该用户"
        }), 400
    
    current_user.follow(user_to_follow)
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "关注成功",
        "data": {
            "is_following": True,
            "user": user_to_follow.to_dict()
        }
    })

@social_bp.route('/api/social/unfollow/<int:user_id>', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = get_jwt_identity()
    
    if int(current_user_id) == user_id:
        return jsonify({
            "code": 400,
            "message": "不能取消关注自己"
        }), 400
    
    current_user = User.query.get(int(current_user_id))
    user_to_unfollow = User.query.get(user_id)
    
    if not current_user:
        return jsonify({
            "code": 404,
            "message": "当前用户不存在"
        }), 404
    
    if not user_to_unfollow:
        return jsonify({
            "code": 404,
            "message": "要取消关注的用户不存在"
        }), 404
    
    if not current_user.is_following(user_to_unfollow):
        return jsonify({
            "code": 400,
            "message": "没有关注该用户"
        }), 400
    
    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "取消关注成功",
        "data": {
            "is_following": False,
            "user": user_to_unfollow.to_dict()
        }
    })

@social_bp.route('/api/social/block/<int:user_id>', methods=['POST'])
@jwt_required()
def block_user(user_id):
    current_user_id = get_jwt_identity()
    
    if int(current_user_id) == user_id:
        return jsonify({
            "code": 400,
            "message": "不能拉黑自己"
        }), 400
    
    current_user = User.query.get(int(current_user_id))
    user_to_block = User.query.get(user_id)
    
    if not current_user:
        return jsonify({
            "code": 404,
            "message": "当前用户不存在"
        }), 404
    
    if not user_to_block:
        return jsonify({
            "code": 404,
            "message": "要拉黑的用户不存在"
        }), 404
    
    if current_user.is_blocking(user_to_block):
        return jsonify({
            "code": 400,
            "message": "已经拉黑了该用户"
        }), 400
    
    # Unfollow if following
    if current_user.is_following(user_to_block):
        current_user.unfollow(user_to_block)
    
    # Remove from follower if followed by
    if user_to_block.is_following(current_user):
        user_to_block.unfollow(current_user)
    
    current_user.block(user_to_block)
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "拉黑成功",
        "data": {
            "is_blocked": True,
            "user": user_to_block.to_dict()
        }
    })

@social_bp.route('/api/social/unblock/<int:user_id>', methods=['POST'])
@jwt_required()
def unblock_user(user_id):
    current_user_id = get_jwt_identity()
    
    if int(current_user_id) == user_id:
        return jsonify({
            "code": 400,
            "message": "不能取消拉黑自己"
        }), 400
    
    current_user = User.query.get(int(current_user_id))
    user_to_unblock = User.query.get(user_id)
    
    if not current_user:
        return jsonify({
            "code": 404,
            "message": "当前用户不存在"
        }), 404
    
    if not user_to_unblock:
        return jsonify({
            "code": 404,
            "message": "要取消拉黑的用户不存在"
        }), 404
    
    if not current_user.is_blocking(user_to_unblock):
        return jsonify({
            "code": 400,
            "message": "没有拉黑该用户"
        }), 400
    
    current_user.unblock(user_to_unblock)
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "取消拉黑成功",
        "data": {
            "is_blocked": False,
            "user": user_to_unblock.to_dict()
        }
    })

@social_bp.route('/api/social/blocklist', methods=['GET'])
@jwt_required()
def get_blocklist():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    if not current_user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    # Get blocked users
    blocklist = Blacklist.query.filter_by(user_id=int(current_user_id))\
        .order_by(Blacklist.created_at.desc())\
        .paginate(page=page, per_page=page_size, error_out=False)
    
    blocked_users = []
    for block in blocklist.items:
        user = User.query.get(block.blacklisted_user_id)
        if user:
            user_dict = user.to_dict()
            user_dict['blocked_at'] = block.created_at.isoformat() + 'Z'
            user_dict['block_reason'] = block.reason or ''
            blocked_users.append(user_dict)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "blocked_users": blocked_users,
            "total": blocklist.total,
            "page": page,
            "page_size": page_size,
            "has_more": blocklist.has_next
        }
    })

@social_bp.route('/api/social/followers/<int:user_id>', methods=['GET'])
def get_followers(user_id):
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
    
    # Check if current user is following each follower
    current_user = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        if current_user_id:
            current_user = User.query.get(int(current_user_id))
    except:
        pass
    
    follower_list = []
    for follow in followers.items:
        follower = User.query.get(follow.follower_id)
        if follower:
            follower_dict = follower.to_dict()
            follower_dict['followed_at'] = follow.created_at.isoformat() + 'Z'
            if current_user:
                follower_dict['is_following'] = current_user.is_following(follower)
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

@social_bp.route('/api/social/following/<int:user_id>', methods=['GET'])
def get_following(user_id):
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
    
    # Check if current user is following each followed user
    current_user = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        if current_user_id:
            current_user = User.query.get(int(current_user_id))
    except:
        pass
    
    following_list = []
    for follow in following.items:
        followed_user = User.query.get(follow.followed_id)
        if followed_user:
            user_dict = followed_user.to_dict()
            user_dict['followed_at'] = follow.created_at.isoformat() + 'Z'
            if current_user and current_user.id != user_id:
                user_dict['is_following'] = current_user.is_following(followed_user)
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

@social_bp.route('/api/social/relation/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
def get_relation(user_id):
    current_user_id = get_jwt_identity()
    target_user = User.query.get(user_id)
    
    if not target_user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    relation = {
        "is_following": False,
        "is_followed": False,
        "is_blocked": False,
        "is_blocking": False
    }
    
    if current_user_id:
        current_user = User.query.get(int(current_user_id))
        if current_user:
            relation['is_following'] = current_user.is_following(target_user)
            relation['is_followed'] = target_user.is_following(current_user)
            relation['is_blocked'] = target_user.is_blocking(current_user)
            relation['is_blocking'] = current_user.is_blocking(target_user)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": relation
    })
