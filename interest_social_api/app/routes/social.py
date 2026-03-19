from flask import Blueprint, request, jsonify
from app.models.database import db, User, Follow, Blacklist, Notification
from app.routes.auth import token_required

social_bp = Blueprint('social', __name__)

@social_bp.route('/api/social/follow/<int:user_id>', methods=['POST'])
@token_required
def follow_user(current_user, user_id):
    if user_id == current_user.id:
        return jsonify({
            'code': 400,
            'message': '不能关注自己',
            'data': None
        }), 400
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({
            'code': 404,
            'message': '用户不存在',
            'data': None
        }), 404
    
    blocked = Blacklist.query.filter_by(user_id=user_id, blocked_user_id=current_user.id).first()
    if blocked:
        return jsonify({
            'code': 403,
            'message': '无法关注该用户',
            'data': None
        }), 403
    
    existing_follow = Follow.query.filter_by(
        follower_id=current_user.id, 
        followed_id=user_id
    ).first()
    
    if existing_follow:
        return jsonify({
            'code': 400,
            'message': '已经关注了该用户',
            'data': None
        }), 400
    
    new_follow = Follow(follower_id=current_user.id, followed_id=user_id)
    db.session.add(new_follow)
    
    notification = Notification(
        user_id=user_id,
        type='follow',
        title=f'{current_user.nickname} 关注了你',
        content='',
        sender_id=current_user.id
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '关注成功',
        'data': {
            'is_following': True,
            'followers_count': target_user.followers.count()
        }
    })

@social_bp.route('/api/social/unfollow/<int:user_id>', methods=['POST'])
@token_required
def unfollow_user(current_user, user_id):
    if user_id == current_user.id:
        return jsonify({
            'code': 400,
            'message': '不能取消关注自己',
            'data': None
        }), 400
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({
            'code': 404,
            'message': '用户不存在',
            'data': None
        }), 404
    
    existing_follow = Follow.query.filter_by(
        follower_id=current_user.id, 
        followed_id=user_id
    ).first()
    
    if not existing_follow:
        return jsonify({
            'code': 400,
            'message': '未关注该用户',
            'data': None
        }), 400
    
    db.session.delete(existing_follow)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '取消关注成功',
        'data': {
            'is_following': False,
            'followers_count': target_user.followers.count()
        }
    })

@social_bp.route('/api/social/following/<int:user_id>', methods=['GET'])
def get_user_following(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'code': 404,
            'message': '用户不存在',
            'data': None
        }), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Follow.query.filter_by(follower_id=user_id)\
        .order_by(Follow.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    following = [follow.to_dict() for follow in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'following': following,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next
        }
    })

@social_bp.route('/api/social/followers/<int:user_id>', methods=['GET'])
def get_user_followers(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'code': 404,
            'message': '用户不存在',
            'data': None
        }), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Follow.query.filter_by(followed_id=user_id)\
        .order_by(Follow.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    followers_list = []
    for follow in pagination.items:
        follower_user = User.query.get(follow.follower_id)
        if follower_user:
            is_following = Follow.query.filter_by(
                follower_id=user_id, 
                followed_id=follow.follower_id
            ).first() is not None
            
            followers_list.append({
                'id': follower_user.id,
                'nickname': follower_user.nickname,
                'avatar': follower_user.avatar or f'https://picsum.photos/200/200?random={follower_user.id}',
                'bio': follower_user.bio,
                'is_following': is_following,
                'followed_at': follow.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if follow.created_at else None
            })
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'followers': followers_list,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next
        }
    })

@social_bp.route('/api/social/blacklist', methods=['GET'])
@token_required
def get_blacklist(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Blacklist.query.filter_by(user_id=current_user.id)\
        .order_by(Blacklist.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    blacklist = [item.to_dict() for item in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'blacklist': blacklist,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next
        }
    })

@social_bp.route('/api/social/blacklist/<int:user_id>', methods=['POST'])
@token_required
def add_to_blacklist(current_user, user_id):
    if user_id == current_user.id:
        return jsonify({
            'code': 400,
            'message': '不能将自己加入黑名单',
            'data': None
        }), 400
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({
            'code': 404,
            'message': '用户不存在',
            'data': None
        }), 404
    
    existing = Blacklist.query.filter_by(
        user_id=current_user.id, 
        blocked_user_id=user_id
    ).first()
    
    if existing:
        return jsonify({
            'code': 400,
            'message': '该用户已在黑名单中',
            'data': None
        }), 400
    
    follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
    if follow:
        db.session.delete(follow)
    
    follow_back = Follow.query.filter_by(follower_id=user_id, followed_id=current_user.id).first()
    if follow_back:
        db.session.delete(follow_back)
    
    new_blacklist = Blacklist(user_id=current_user.id, blocked_user_id=user_id)
    db.session.add(new_blacklist)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '已加入黑名单',
        'data': {
            'is_blocked': True
        }
    })

@social_bp.route('/api/social/blacklist/<int:user_id>', methods=['DELETE'])
@token_required
def remove_from_blacklist(current_user, user_id):
    existing = Blacklist.query.filter_by(
        user_id=current_user.id, 
        blocked_user_id=user_id
    ).first()
    
    if not existing:
        return jsonify({
            'code': 404,
            'message': '该用户不在黑名单中',
            'data': None
        }), 404
    
    db.session.delete(existing)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '已移出黑名单',
        'data': {
            'is_blocked': False
        }
    })

@social_bp.route('/api/social/check-follow/<int:user_id>', methods=['GET'])
@token_required
def check_follow_status(current_user, user_id):
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({
            'code': 404,
            'message': '用户不存在',
            'data': None
        }), 404
    
    is_following = Follow.query.filter_by(
        follower_id=current_user.id, 
        followed_id=user_id
    ).first() is not None
    
    is_followed = Follow.query.filter_by(
        follower_id=user_id, 
        followed_id=current_user.id
    ).first() is not None
    
    is_blocked = Blacklist.query.filter_by(
        user_id=current_user.id, 
        blocked_user_id=user_id
    ).first() is not None
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'is_following': is_following,
            'is_followed': is_followed,
            'is_blocked': is_blocked
        }
    })
