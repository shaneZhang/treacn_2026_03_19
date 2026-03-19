from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(500), default='')
    bio = db.Column(db.String(500), default='')
    gender = db.Column(db.Integer, default=0)
    birthday = db.Column(db.String(20), default='')
    location = db.Column(db.String(100), default='')
    is_verified = db.Column(db.Boolean, default=False)
    verified_type = db.Column(db.String(50), default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'bio': self.bio,
            'gender': self.gender,
            'birthday': self.birthday,
            'location': self.location,
            'is_verified': self.is_verified,
            'verified_type': self.verified_type,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text, default='[]')
    topic = db.Column(db.String(100), default='', index=True)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.author.nickname if self.author else '',
            'user_avatar': self.author.avatar if self.author else '',
            'content': self.content,
            'images': json.loads(self.images) if self.images else [],
            'topic': self.topic,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None,
            'is_deleted': self.is_deleted
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), default=None)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'username': self.author.nickname if self.author else '',
            'user_avatar': self.author.avatar if self.author else '',
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }

class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

class Follow(db.Model):
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id', name='unique_follow'),)

class Blacklist(db.Model):
    __tablename__ = 'blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    blocked_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'blocked_user_id', name='unique_block'),)

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(500), default='')
    posts_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'posts_count': self.posts_count,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }

class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    size = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'url': self.url,
            'size': self.size,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }
