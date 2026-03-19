import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.models.database import db, Post, Comment, Like, User, Notification
from app.routes.auth import token_required

post_bp = Blueprint('post', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@post_bp.route('/api/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    topic = request.args.get('topic', '')
    user_id = request.args.get('user_id', type=int)
    
    query = Post.query.filter_by(is_deleted=False)
    
    if topic:
        query = query.filter(Post.topic.contains(topic))
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts = [post.to_dict() for post in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'posts': posts,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next
        }
    })

@post_bp.route('/api/posts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.get_json()
    
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求数据不能为空',
            'data': None
        }), 400
    
    content = data.get('content', '').strip()
    images = data.get('images', [])
    topic = data.get('topic', '')
    
    if not content:
        return jsonify({
            'code': 400,
            'message': '帖子内容不能为空',
            'data': None
        }), 400
    
    if len(content) > 5000:
        return jsonify({
            'code': 400,
            'message': '帖子内容不能超过5000个字符',
            'data': None
        }), 400
    
    images_str = ','.join(images) if isinstance(images, list) else images
    
    new_post = Post(
        user_id=current_user.id,
        content=content,
        images=images_str,
        topic=topic
    )
    
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '发布成功',
        'data': new_post.to_dict(current_user.id)
    }), 201

@post_bp.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.filter_by(id=post_id, is_deleted=False).first()
    
    if not post:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header:
        import jwt
        try:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
        except:
            pass
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': post.to_dict(user_id)
    })

@post_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    post = Post.query.filter_by(id=post_id, is_deleted=False).first()
    
    if not post:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    if post.user_id != current_user.id:
        return jsonify({
            'code': 403,
            'message': '无权删除此帖子',
            'data': None
        }), 403
    
    post.is_deleted = True
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功',
        'data': None
    })

@post_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
@token_required
def toggle_like(current_user, post_id):
    post = Post.query.filter_by(id=post_id, is_deleted=False).first()
    
    if not post:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '取消点赞成功',
            'data': {
                'is_liked': False,
                'likes_count': post.likes.count()
            }
        })
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        
        if post.user_id != current_user.id:
            notification = Notification(
                user_id=post.user_id,
                type='like',
                title=f'{current_user.nickname} 点赞了你的帖子',
                content=post.content[:50] + '...' if len(post.content) > 50 else post.content,
                related_id=post.id,
                sender_id=current_user.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '点赞成功',
            'data': {
                'is_liked': True,
                'likes_count': post.likes.count()
            }
        })

@post_bp.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = Post.query.filter_by(id=post_id, is_deleted=False).first()
    
    if not post:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Comment.query.filter_by(post_id=post_id, is_deleted=False)\
        .order_by(Comment.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    comments = [comment.to_dict() for comment in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'comments': comments,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next
        }
    })

@post_bp.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(current_user, post_id):
    post = Post.query.filter_by(id=post_id, is_deleted=False).first()
    
    if not post:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求数据不能为空',
            'data': None
        }), 400
    
    content = data.get('content', '').strip()
    reply_to_id = data.get('reply_to_id')
    
    if not content:
        return jsonify({
            'code': 400,
            'message': '评论内容不能为空',
            'data': None
        }), 400
    
    if len(content) > 500:
        return jsonify({
            'code': 400,
            'message': '评论内容不能超过500个字符',
            'data': None
        }), 400
    
    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=content,
        reply_to_id=reply_to_id
    )
    
    db.session.add(new_comment)
    
    if post.user_id != current_user.id:
        notification = Notification(
            user_id=post.user_id,
            type='comment',
            title=f'{current_user.nickname} 评论了你的帖子',
            content=content,
            related_id=post.id,
            sender_id=current_user.id
        )
        db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '评论成功',
        'data': new_comment.to_dict()
    }), 201

@post_bp.route('/api/upload', methods=['POST'])
@token_required
def upload_image(current_user):
    if 'file' not in request.files:
        return jsonify({
            'code': 400,
            'message': '没有上传文件',
            'data': None
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'code': 400,
            'message': '没有选择文件',
            'data': None
        }), 400
    
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'url': f'/uploads/{filename}',
                'filename': filename
            }
        })
    
    return jsonify({
        'code': 400,
        'message': '不支持的文件类型',
        'data': None
    }), 400
