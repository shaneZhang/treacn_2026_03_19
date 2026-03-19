from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

from app.models.database import db, User, TokenBlacklist

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'code': 401,
                'message': '缺少认证令牌',
                'data': None
            }), 401
        
        blacklisted = TokenBlacklist.query.filter_by(token=token).first()
        if blacklisted:
            return jsonify({
                'code': 401,
                'message': '令牌已失效，请重新登录',
                'data': None
            }), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({
                'code': 401,
                'message': '令牌无效或已过期',
                'data': None
            }), 401
        
        current_user = User.query.get(payload['user_id'])
        if not current_user:
            return jsonify({
                'code': 401,
                'message': '用户不存在',
                'data': None
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()
    
    if not username or not password:
        return jsonify({
            'code': 400,
            'message': '用户名和密码不能为空',
            'data': None
        }), 400
    
    if len(username) < 3 or len(username) > 50:
        return jsonify({
            'code': 400,
            'message': '用户名长度必须在3-50个字符之间',
            'data': None
        }), 400
    
    if len(password) < 6:
        return jsonify({
            'code': 400,
            'message': '密码长度不能少于6个字符',
            'data': None
        }), 400
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({
            'code': 400,
            'message': '用户名已存在',
            'data': None
        }), 400
    
    if not nickname:
        nickname = username
    
    password_hash = generate_password_hash(password)
    
    user = User(
        username=username,
        password_hash=password_hash,
        nickname=nickname,
        avatar=data.get('avatar', ''),
        bio=data.get('bio', ''),
        gender=data.get('gender', 0),
        birthday=data.get('birthday', ''),
        location=data.get('location', '')
    )
    
    db.session.add(user)
    db.session.commit()
    
    token = generate_token(user.id)
    
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': {
            'user': user.to_dict(),
            'token': token,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({
            'code': 400,
            'message': '用户名和密码不能为空',
            'data': None
        }), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({
            'code': 401,
            'message': '用户名或密码错误',
            'data': None
        }), 401
    
    if not check_password_hash(user.password_hash, password):
        return jsonify({
            'code': 401,
            'message': '用户名或密码错误',
            'data': None
        }), 401
    
    if not user.is_active:
        return jsonify({
            'code': 403,
            'message': '账户已被禁用',
            'data': None
        }), 403
    
    token = generate_token(user.id)
    
    from app.models.database import Follow, Like, Post
    followers_count = Follow.query.filter_by(following_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()
    posts_count = user.posts.filter_by(is_deleted=False).count()
    likes_count = db.session.query(Like).join(Post).filter(Post.user_id == user.id).count()
    
    user_data = user.to_dict()
    user_data['followers_count'] = followers_count
    user_data['following_count'] = following_count
    user_data['posts_count'] = posts_count
    user_data['likes_count'] = likes_count
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user': user_data,
            'token': token,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if token:
        blacklisted_token = TokenBlacklist(
            token=token,
            user_id=current_user.id
        )
        db.session.add(blacklisted_token)
        db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '登出成功',
        'data': None
    })

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    return jsonify({
        'code': 200,
        'message': '令牌有效',
        'data': {
            'user': current_user.to_dict(),
            'is_valid': True
        }
    })

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json()
    
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not old_password or not new_password:
        return jsonify({
            'code': 400,
            'message': '旧密码和新密码不能为空',
            'data': None
        }), 400
    
    if len(new_password) < 6:
        return jsonify({
            'code': 400,
            'message': '新密码长度不能少于6个字符',
            'data': None
        }), 400
    
    if not check_password_hash(current_user.password_hash, old_password):
        return jsonify({
            'code': 401,
            'message': '旧密码错误',
            'data': None
        }), 401
    
    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '密码修改成功',
        'data': None
    })
