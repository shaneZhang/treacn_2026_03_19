from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(500), default='')
    bio = db.Column(db.String(500), default='')
    gender = db.Column(db.Integer, default=0)
    birthday = db.Column(db.String(20), default='')
    location = db.Column(db.String(100), default='')
    is_verified = db.Column(db.Boolean, default=False)
    verified_type = db.Column(db.String(50), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy='dynamic')
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic')
    blacklist = db.relationship('Blacklist', foreign_keys='Blacklist.user_id', backref='blocker', lazy='dynamic')
    blocked_by = db.relationship('Blacklist', foreign_keys='Blacklist.blocked_user_id', backref='blocked', lazy='dynamic')
    tokens = db.relationship('Token', backref='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar or f'https://picsum.photos/200/200?random={self.id}',
            'bio': self.bio,
            'gender': self.gender,
            'birthday': self.birthday,
            'location': self.location,
            'followers_count': self.followers.count(),
            'following_count': self.following.count(),
            'posts_count': self.posts.count(),
            'likes_count': db.session.query(Like).join(Post).filter(Post.user_id == self.id).count(),
            'is_verified': self.is_verified,
            'verified_type': self.verified_type,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }
    
    def to_simple_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'avatar': self.avatar or f'https://picsum.photos/200/200?random={self.id}',
            'bio': self.bio
        }


class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text, default='')
    topic = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    
    def to_dict(self, current_user_id=None):
        is_liked = False
        if current_user_id:
            is_liked = Like.query.filter_by(user_id=current_user_id, post_id=self.id).first() is not None
        
        author = User.query.get(self.user_id)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': author.nickname if author else '',
            'user_avatar': author.avatar if author else '',
            'content': self.content,
            'images': self.images.split(',') if self.images else [],
            'topic': self.topic,
            'likes_count': self.likes.count(),
            'comments_count': self.comments.count(),
            'shares_count': 0,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None,
            'is_liked': is_liked
        }


class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        author = User.query.get(self.user_id)
        reply_to = None
        if self.reply_to_id:
            reply_comment = Comment.query.get(self.reply_to_id)
            if reply_comment:
                reply_user = User.query.get(reply_comment.user_id)
                reply_to = {
                    'id': reply_comment.id,
                    'user_id': reply_comment.user_id,
                    'nickname': reply_user.nickname if reply_user else ''
                }
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'nickname': author.nickname if author else '',
            'avatar': author.avatar if author else '',
            'content': self.content,
            'reply_to': reply_to,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }


class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)


class Follow(db.Model):
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id'),)
    
    def to_dict(self):
        followed_user = User.query.get(self.followed_id)
        return {
            'id': followed_user.id,
            'nickname': followed_user.nickname,
            'avatar': followed_user.avatar or f'https://picsum.photos/200/200?random={followed_user.id}',
            'bio': followed_user.bio,
            'is_following': True,
            'followed_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }


class Blacklist(db.Model):
    __tablename__ = 'blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blocked_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'blocked_user_id'),)
    
    def to_dict(self):
        blocked_user = User.query.get(self.blocked_user_id)
        return {
            'id': blocked_user.id,
            'nickname': blocked_user.nickname,
            'avatar': blocked_user.avatar or f'https://picsum.photos/200/200?random={blocked_user.id}',
            'bio': blocked_user.bio,
            'blocked_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }


class Token(db.Model):
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)


class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    posts_count = db.Column(db.Integer, default=0)
    trend = db.Column(db.String(20), default='stable')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'posts_count': self.posts_count,
            'trend': self.trend
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='')
    related_id = db.Column(db.Integer, default=0)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    
    def to_dict(self):
        sender = User.query.get(self.sender_id) if self.sender_id else None
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'related_id': self.related_id,
            'sender': sender.to_simple_dict() if sender else None,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None
        }
