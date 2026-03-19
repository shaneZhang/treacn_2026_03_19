import jwt
import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import db, User, Token

auth_bp = Blueprint('auth', __name__)

def generate_token(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(
        hours=current_app.config['JWT_EXPIRATION_HOURS']
    )
    payload = {
        'user_id': user_id,
        'exp': expiration,
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    token_record = Token(
        user_id=user_id,
        token=token,
        expires_at=expiration,
        is_valid=True
    )
    db.session.add(token_record)
    db.session.commit()
    
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
        
        if not token:
            return jsonify({
                'code': 401,
                'message': '缺少认证令牌',
                'data': None
            }), 401
        
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            token_record = Token.query.filter_by(token=token, user_id=user_id, is_valid=True).first()
            if not token_record:
                return jsonify({
                    'code': 401,
                    'message': '无效的令牌',
                    'data': None
                }), 401
            
            if token_record.expires_at < datetime.datetime.utcnow():
                token_record.is_valid = False
                db.session.commit()
                return jsonify({
                    'code': 401,
                    'message': '令牌已过期',
                    'data': None
                }), 401
            
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({
                    'code': 401,
                    'message': '用户不存在',
                    'data': None
                }), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({
                'code': 401,
                'message': '令牌已过期',
                'data': None
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'code': 401,
                'message': '无效的令牌',
                'data': None
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求数据不能为空',
            'data': None
        }), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()
    
    if not username:
        return jsonify({
            'code': 400,
            'message': '用户名不能为空',
            'data': None
        }), 400
    
    if not password:
        return jsonify({
            'code': 400,
            'message': '密码不能为空',
            'data': None
        }), 400
    
    if len(username) < 3 or len(username) > 20:
        return jsonify({
            'code': 400,
            'message': '用户名长度需在3-20个字符之间',
            'data': None
        }), 400
    
    if len(password) < 6:
        return jsonify({
            'code': 400,
            'message': '密码长度至少6个字符',
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
    
    new_user = User(
        username=username,
        password_hash=password_hash,
        nickname=nickname,
        bio=data.get('bio', ''),
        gender=data.get('gender', 0),
        birthday=data.get('birthday', ''),
        location=data.get('location', '')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    token = generate_token(new_user.id)
    
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': {
            'user': new_user.to_dict(),
            'token': token
        }
    }), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求数据不能为空',
            'data': None
        }), 400
    
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
    
    token = generate_token(user.id)
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user': user.to_dict(),
            'token': token
        }
    })

@auth_bp.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = auth_header
        
        token_record = Token.query.filter_by(token=token, user_id=current_user.id).first()
        if token_record:
            token_record.is_valid = False
            db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '登出成功',
        'data': None
    })

@auth_bp.route('/api/auth/verify', methods=['GET'])
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

@auth_bp.route('/api/auth/password', methods=['PUT'])
@token_required
def change_password(current_user):
    data = request.get_json()
    
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求数据不能为空',
            'data': None
        }), 400
    
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
            'message': '新密码长度至少6个字符',
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
    
    Token.query.filter_by(user_id=current_user.id, is_valid=True).update({'is_valid': False})
    db.session.commit()
    
    new_token = generate_token(current_user.id)
    
    return jsonify({
        'code': 200,
        'message': '密码修改成功',
        'data': {
            'token': new_token
        }
    })
