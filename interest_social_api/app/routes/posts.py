from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Post, Comment, Like, Topic
from datetime import datetime
import os
import json
import uuid
from werkzeug.utils import secure_filename

posts_bp = Blueprint('posts', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posts_bp.route('/api/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    topic = request.args.get('topic')
    
    query = Post.query.filter_by(is_public=True)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if topic:
        query = query.filter(Post.topic.like(f'%{topic}%'))
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    # Get current user if authenticated
    current_user = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        if current_user_id:
            current_user = User.query.get(int(current_user_id))
    except:
        pass
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "posts": [post.to_dict(current_user) for post in posts.items],
            "total": posts.total,
            "page": page,
            "page_size": page_size,
            "has_more": posts.has_next
        }
    })

@posts_bp.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({
            "code": 400,
            "message": "请输入帖子内容"
        }), 400
    
    content = data['content'].strip()
    if not content:
        return jsonify({
            "code": 400,
            "message": "帖子内容不能为空"
        }), 400
    
    images = data.get('images', [])
    if isinstance(images, list):
        images_json = json.dumps(images)
    else:
        images_json = json.dumps([])
    
    post = Post(
        user_id=int(current_user_id),
        content=content,
        images=images_json,
        topic=data.get('topic'),
        location=data.get('location'),
        is_public=data.get('is_public', True)
    )
    
    db.session.add(post)
    
    # Update topic post count
    if data.get('topic'):
        topic = Topic.query.filter_by(name=data['topic']).first()
        if topic:
            topic.posts_count += 1
        else:
            new_topic = Topic(name=data['topic'], posts_count=1)
            db.session.add(new_topic)
    
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "发布成功",
        "data": {
            "post": post.to_dict(user)
        }
    }), 201

@posts_bp.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({
            "code": 404,
            "message": "帖子不存在"
        }), 404
    
    if not post.is_public:
        # Check if user is authorized to view private post
        current_user = None
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
            if current_user_id:
                current_user = User.query.get(int(current_user_id))
        except:
            pass
        
        if not current_user or current_user.id != post.user_id:
            return jsonify({
                "code": 403,
                "message": "无权查看该帖子"
            }), 403
    
    # Get current user if authenticated
    current_user = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        if current_user_id:
            current_user = User.query.get(int(current_user_id))
    except:
        pass
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "post": post.to_dict(current_user)
        }
    })

@posts_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({
            "code": 404,
            "message": "帖子不存在"
        }), 404
    
    if post.user_id != current_user_id:
        return jsonify({
            "code": 403,
            "message": "无权删除该帖子"
        }), 403
    
    # Update topic post count
    if post.topic:
        topic = Topic.query.filter_by(name=post.topic).first()
        if topic and topic.posts_count > 0:
            topic.posts_count -= 1
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "删除成功"
    })

@posts_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def toggle_like(post_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    post = Post.query.get(post_id)
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    if not post:
        return jsonify({
            "code": 404,
            "message": "帖子不存在"
        }), 404
    
    existing_like = Like.query.filter_by(user_id=int(current_user_id), post_id=post_id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        is_liked = False
        message = "取消点赞成功"
    else:
        # Like
        like = Like(user_id=int(current_user_id), post_id=post_id)
        db.session.add(like)
        is_liked = True
        message = "点赞成功"
    
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": message,
        "data": {
            "is_liked": is_liked,
            "likes_count": post.likes_count
        }
    })

@posts_bp.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({
            "code": 404,
            "message": "帖子不存在"
        }), 404
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None)\
        .order_by(Comment.created_at.desc())\
        .paginate(page=page, per_page=page_size, error_out=False)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "comments": [comment.to_dict() for comment in comments.items],
            "total": comments.total,
            "page": page,
            "page_size": page_size,
            "has_more": comments.has_next
        }
    })

@posts_bp.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    post = Post.query.get(post_id)
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    if not post:
        return jsonify({
            "code": 404,
            "message": "帖子不存在"
        }), 404
    
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({
            "code": 400,
            "message": "请输入评论内容"
        }), 400
    
    content = data['content'].strip()
    if not content:
        return jsonify({
            "code": 400,
            "message": "评论内容不能为空"
        }), 400
    
    comment = Comment(
        user_id=int(current_user_id),
        post_id=post_id,
        content=content,
        parent_id=data.get('parent_id')
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "message": "评论成功",
        "data": {
            "comment": comment.to_dict()
        }
    }), 201

@posts_bp.route('/api/posts/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在"
        }), 404
    
    if 'image' not in request.files:
        return jsonify({
            "code": 400,
            "message": "没有上传图片"
        }), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({
            "code": 400,
            "message": "没有选择图片"
        }), 400
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{uuid.uuid4()}.{ext}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        
        # Return URL (in production, use actual domain)
        image_url = f"/uploads/{filename}"
        
        return jsonify({
            "code": 200,
            "message": "上传成功",
            "data": {
                "url": image_url,
                "filename": filename
            }
        })
    else:
        return jsonify({
            "code": 400,
            "message": "不支持的图片格式"
        }), 400
