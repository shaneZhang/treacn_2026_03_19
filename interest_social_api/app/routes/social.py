from flask import Blueprint, jsonify, request
from datetime import datetime

from app.models.database import db, User, Follow, Blacklist
from app.routes.auth import token_required

social_bp = Blueprint('social', __name__, url_prefix='/api/social')

@social_bp.route('/follow/<int:user_id>', methods=['POST'])
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
        following_id=user_id
    ).first()
    
    if existing_follow:
        return jsonify({
            'code': 400,
            'message': '已经关注了该用户',
            'data': None
        }), 400
    
    follow = Follow(
        follower_id=current_user.id,
        following_id=user_id
    )
    
    db.session.add(follow)
    db.session.commit()
    
    followers_count = Follow.query.filter_by(following_id=user_id).count()
    following_count = Follow.query.filter_by(follower_id=current_user.id).count()
    
    return jsonify({
        'code': 200,
        'message': '关注成功',
        'data': {
            'is_following': True,
            'followers_count': followers_count,
            'following_count': following_count
        }
    })

@social_bp.route('/unfollow/<int:user_id>', methods=['POST'])
@token_required
def unfollow_user(current_user, user_id):
    follow = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()
    
    if not follow:
        return jsonify({
            'code': 400,
            'message': '未关注该用户',
            'data': None
        }), 400
    
    db.session.delete(follow)
    db.session.commit()
    
    followers_count = Follow.query.filter_by(following_id=user_id).count()
    following_count = Follow.query.filter_by(follower_id=current_user.id).count()
    
    return jsonify({
        'code': 200,
        'message': '取消关注成功',
        'data': {
            'is_following': False,
            'followers_count': followers_count,
            'following_count': following_count
        }
    })

@social_bp.route('/following', methods=['GET'])
@token_required
def get_following(current_user):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    following_ids = db.session.query(Follow.following_id).filter(
        Follow.follower_id == current_user.id
    ).subquery()
    
    pagination = User.query.filter(User.id.in_(following_ids)).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    following_list = []
    for user in pagination.items:
        user_data = user.to_dict()
        user_data['followed_at'] = Follow.query.filter_by(
            follower_id=current_user.id,
            following_id=user.id
        ).first().created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        following_list.append(user_data)
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'following': following_list,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }
    })

@social_bp.route('/followers', methods=['GET'])
@token_required
def get_followers(current_user):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    follower_ids = db.session.query(Follow.follower_id).filter(
        Follow.following_id == current_user.id
    ).subquery()
    
    pagination = User.query.filter(User.id.in_(follower_ids)).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    followers_list = []
    for user in pagination.items:
        user_data = user.to_dict()
        follow_record = Follow.query.filter_by(
            follower_id=user.id,
            following_id=current_user.id
        ).first()
        if follow_record:
            user_data['followed_at'] = follow_record.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        is_following = Follow.query.filter_by(
            follower_id=current_user.id,
            following_id=user.id
        ).first() is not None
        user_data['is_following'] = is_following
        
        followers_list.append(user_data)
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'followers': followers_list,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }
    })

@social_bp.route('/blacklist/<int:user_id>', methods=['POST'])
@token_required
def add_to_blacklist(current_user, user_id):
    if user_id == current_user.id:
        return jsonify({
            'code': 400,
            'message': '不能拉黑自己',
            'data': None
        }), 400
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({
            'code': 404,
            'message': '用户不存在',
            'data': None
        }), 404
    
    existing_block = Blacklist.query.filter_by(
        user_id=current_user.id,
        blocked_user_id=user_id
    ).first()
    
    if existing_block:
        return jsonify({
            'code': 400,
            'message': '已经拉黑了该用户',
            'data': None
        }), 400
    
    follow = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()
    if follow:
        db.session.delete(follow)
    
    reverse_follow = Follow.query.filter_by(
        follower_id=user_id,
        following_id=current_user.id
    ).first()
    if reverse_follow:
        db.session.delete(reverse_follow)
    
    blacklist = Blacklist(
        user_id=current_user.id,
        blocked_user_id=user_id
    )
    
    db.session.add(blacklist)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '拉黑成功',
        'data': {
            'is_blocked': True
        }
    })

@social_bp.route('/unblacklist/<int:user_id>', methods=['POST'])
@token_required
def remove_from_blacklist(current_user, user_id):
    blacklist = Blacklist.query.filter_by(
        user_id=current_user.id,
        blocked_user_id=user_id
    ).first()
    
    if not blacklist:
        return jsonify({
            'code': 400,
            'message': '未拉黑该用户',
            'data': None
        }), 400
    
    db.session.delete(blacklist)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '取消拉黑成功',
        'data': {
            'is_blocked': False
        }
    })

@social_bp.route('/blacklist', methods=['GET'])
@token_required
def get_blacklist(current_user):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    blocked_ids = db.session.query(Blacklist.blocked_user_id).filter(
        Blacklist.user_id == current_user.id
    ).subquery()
    
    pagination = User.query.filter(User.id.in_(blocked_ids)).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    blacklist_users = []
    for user in pagination.items:
        user_data = user.to_dict()
        blacklist_record = Blacklist.query.filter_by(
            user_id=current_user.id,
            blocked_user_id=user.id
        ).first()
        if blacklist_record:
            user_data['blocked_at'] = blacklist_record.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        blacklist_users.append(user_data)
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'blacklist': blacklist_users,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }
    })

@social_bp.route('/check-follow/<int:user_id>', methods=['GET'])
@token_required
def check_follow_status(current_user, user_id):
    is_following = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first() is not None
    
    is_blocked = Blacklist.query.filter_by(
        user_id=current_user.id,
        blocked_user_id=user_id
    ).first() is not None
    
    is_blocked_by = Blacklist.query.filter_by(
        user_id=user_id,
        blocked_user_id=current_user.id
    ).first() is not None
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'is_following': is_following,
            'is_blocked': is_blocked,
            'is_blocked_by': is_blocked_by
        }
    })
