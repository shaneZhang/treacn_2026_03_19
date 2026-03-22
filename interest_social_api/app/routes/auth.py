from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.utils.security import (
    verify_password,
    hash_password,
    input_validation,
    sanitize_input
)
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# 模拟用户数据库（生产环境应使用真实数据库
mock_users = {
    "user1": {
        "id": 1,
        "username": "user1",
        "password_hash": hash_password("password123"),
        "email": "user1@example.com",
        "role": "user",
        "created_at": datetime.now().isoformat()
    },
    "admin": {
        "id": 2,
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "email": "admin@example.com",
        "role": "admin",
        "created_at": datetime.now().isoformat()
    }
}

# 存储已撤销的token（生产环境应使用Redis
revoked_tokens = set()

@auth_bp.route('/login', methods=['POST'])
@input_validation
def login():
    """用户登录接口"""
    if not request.is_json:
        return jsonify({
            "code": 400,
            "message": "请求格式必须为JSON",
            "data": None
        }), 400
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            "code": 400,
            "message": "用户名和密码不能为空",
            "data": None
        }), 400
    
    # 清理输入
    username = sanitize_input(username)
    
    # 查找用户
    user = mock_users.get(username)
    if not user or not verify_password(user['password_hash'], password):
        return jsonify({
            "code": 401,
            "message": "用户名或密码错误",
            "data": None
        }), 401
    
    # 创建token
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    
    return jsonify({
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role']
            }
        }
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user = get_jwt_identity()
    
    # 检查refresh token是否被撤销
    jwt_data = get_jwt()
    jti = jwt_data['jti']
    if jti in revoked_tokens:
        return jsonify({
            "code": 401,
            "message": "Token已被撤销",
            "data": None
        }), 401
    
    new_access_token = create_access_token(identity=current_user)
    
    return jsonify({
        "code": 200,
        "message": "Token刷新成功",
        "data": {
            "access_token": new_access_token
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    jwt_data = get_jwt()
    jti = jwt_data['jti']
    
    # 将token加入撤销列表
    revoked_tokens.add(jti)
    
    return jsonify({
        "code": 200,
        "message": "登出成功",
        "data": None
    }), 200

@auth_bp.route('/register', methods=['POST'])
@input_validation
def register():
    """用户注册接口"""
    if not request.is_json:
        return jsonify({
            "code": 400,
            "message": "请求格式必须为JSON",
            "data": None
        }), 400
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({
            "code": 400,
            "message": "用户名、密码和邮箱不能为空",
            "data": None
        }), 400
    
    # 清理输入
    username = sanitize_input(username)
    email = sanitize_input(email)
    
    # 检查用户名是否已存在
    if username in mock_users:
        return jsonify({
            "code": 409,
            "message": "用户名已存在",
            "data": None
        }), 409
    
    # 创建新用户
    new_user = {
        "id": len(mock_users) + 1,
        "username": username,
        "password_hash": hash_password(password),
        "email": email,
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
    
    mock_users[username] = new_user
    
    return jsonify({
        "code": 201,
        "message": "注册成功",
        "data": {
            "user": {
                "id": new_user['id'],
                "username": new_user['username'],
                "email": new_user['email'],
                "role": new_user['role']
            }
        }
    }), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    current_user = get_jwt_identity()
    user = mock_users.get(current_user)
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在",
            "data": None
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "created_at": user['created_at']
        }
    }), 200