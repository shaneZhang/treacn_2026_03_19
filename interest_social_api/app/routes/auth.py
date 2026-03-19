from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app.models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Token blacklist (in production, use Redis)
token_blacklist = set()

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({
            "code": 400,
            "message": "请求数据不能为空"
        }), 400
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必填字段: {field}"
            }), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            "code": 409,
            "message": "用户名已存在"
        }), 409
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            "code": 409,
            "message": "邮箱已被注册"
        }), 409
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        nickname=data.get('nickname', data['username']),
        bio=data.get('bio', ''),
        gender=data.get('gender', 0),
        birthday=data.get('birthday'),
        location=data.get('location', '')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create tokens (identity must be string
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        "code": 200,
        "message": "注册成功",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }
    }), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({
            "code": 400,
            "message": "请求数据不能为空"
        }), 400
    
    # Support both username and email login
    username_or_email = data.get('username') or data.get('email')
    password = data.get('password')
    
    if not username_or_email or not password:
        return jsonify({
            "code": 400,
            "message": "请输入用户名/邮箱和密码"
        }), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == username_or_email) | 
        (User.email == username_or_email)
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({
            "code": 401,
            "message": "用户名/邮箱或密码错误"
        }), 401
    
    # Create tokens (identity must be string
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }
    })

@auth_bp.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        "code": 200,
        "message": "Token刷新成功",
        "data": {
            "access_token": access_token
        }
    })

@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    token_blacklist.add(jti)
    
    return jsonify({
        "code": 200,
        "message": "登出成功"
    })

@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "user": user.to_dict()
        }
    })

@auth_bp.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({
            "code": 400,
            "message": "请输入旧密码和新密码"
        }), 400
    
    if not user.check_password(old_password):
        return jsonify({
            "code": 401,
            "message": "旧密码错误"
        }), 401
    
    if len(new_password) < 6:
        return jsonify({
            "code": 400,
            "message": "新密码长度不能少于6位"
        }), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "密码修改成功"
    })

@auth_bp.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'bio' in data:
        user.bio = data['bio']
    if 'gender' in data:
        user.gender = data['gender']
    if 'birthday' in data:
        user.birthday = data['birthday']
    if 'location' in data:
        user.location = data['location']
    if 'avatar' in data:
        user.avatar = data['avatar']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "资料更新成功",
        "data": {
            "user": user.to_dict()
        }
    })
