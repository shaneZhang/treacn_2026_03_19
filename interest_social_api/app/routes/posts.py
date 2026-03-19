from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime

from app.models.database import db, User, Post, Comment, Like, Image
from app.routes.auth import token_required

posts_bp = Blueprint('posts', __name__, url_prefix='/api')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    topic = request.args.get('topic', '')
    user_id = request.args.get('user_id', type=int)
    
    query = Post.query.filter_by(is_deleted=False)
    
    if topic:
        query = query.filter(Post.topic.like(f'%{topic}%'))
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    query = query.order_by(Post.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    posts = [post.to_dict() for post in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'posts': posts,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }
    })

@posts_bp.route('/posts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.get_json()
    
    content = data.get('content', '').strip()
    images = data.get('images', [])
    topic = data.get('topic', '').strip()
    
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
    
    post = Post(
        user_id=current_user.id,
        content=content,
        images=json.dumps(images) if images else '[]',
        topic=topic
    )
    
    db.session.add(post)
    db.session.commit()
    
    if topic:
        from app.models.database import Topic
        topic_record = Topic.query.filter(Topic.name.like(f'%{topic}%')).first()
        if topic_record:
            topic_record.posts_count += 1
            db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '发布成功',
        'data': {
            'post': post.to_dict()
        }
    }), 201

@posts_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    
    if not post or post.is_deleted:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    post_data = post.to_dict()
    comments = Comment.query.filter_by(post_id=post_id, is_deleted=False).order_by(Comment.created_at.desc()).limit(20).all()
    post_data['comments'] = [comment.to_dict() for comment in comments]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': post_data
    })

@posts_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    post = Post.query.get(post_id)
    
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

@posts_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@token_required
def toggle_like(current_user, post_id):
    post = Post.query.get(post_id)
    
    if not post or post.is_deleted:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        is_liked = False
        message = '取消点赞成功'
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        post.likes_count += 1
        is_liked = True
        message = '点赞成功'
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': message,
        'data': {
            'is_liked': is_liked,
            'likes_count': post.likes_count
        }
    })

@posts_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    post = Post.query.get(post_id)
    if not post or post.is_deleted:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    query = Comment.query.filter_by(post_id=post_id, is_deleted=False).order_by(Comment.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    comments = [comment.to_dict() for comment in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'comments': comments,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }
    })

@posts_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(current_user, post_id):
    data = request.get_json()
    
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')
    
    if not content:
        return jsonify({
            'code': 400,
            'message': '评论内容不能为空',
            'data': None
        }), 400
    
    if len(content) > 1000:
        return jsonify({
            'code': 400,
            'message': '评论内容不能超过1000个字符',
            'data': None
        }), 400
    
    post = Post.query.get(post_id)
    if not post or post.is_deleted:
        return jsonify({
            'code': 404,
            'message': '帖子不存在',
            'data': None
        }), 404
    
    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=content,
        parent_id=parent_id
    )
    
    db.session.add(comment)
    post.comments_count += 1
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '评论成功',
        'data': {
            'comment': comment.to_dict()
        }
    }), 201

@posts_bp.route('/upload/image', methods=['POST'])
@token_required
def upload_image(current_user):
    if 'image' not in request.files:
        return jsonify({
            'code': 400,
            'message': '没有上传图片',
            'data': None
        }), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({
            'code': 400,
            'message': '没有选择文件',
            'data': None
        }), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        user_folder = os.path.join(upload_folder, str(current_user.id))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        filepath = os.path.join(user_folder, new_filename)
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        
        url = f"/uploads/{current_user.id}/{new_filename}"
        
        image = Image(
            user_id=current_user.id,
            filename=new_filename,
            filepath=filepath,
            url=url,
            size=file_size
        )
        
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'image': image.to_dict()
            }
        })
    
    return jsonify({
        'code': 400,
        'message': '不支持的文件格式',
        'data': None
    }), 400
