from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(80))
    avatar = db.Column(db.String(255))
    bio = db.Column(db.Text)
    gender = db.Column(db.Integer, default=0)  # 0: unknown, 1: male, 2: female
    birthday = db.Column(db.String(20))
    location = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    verified_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    
    # Follow relationships
    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref='follower',
        lazy='dynamic'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref='followed',
        lazy='dynamic'
    )
    
    # Blacklist relationships
    blacklisted = db.relationship(
        'Blacklist',
        foreign_keys='Blacklist.user_id',
        backref='user',
        lazy='dynamic'
    )
    blacklisted_by = db.relationship(
        'Blacklist',
        foreign_keys='Blacklist.blacklisted_user_id',
        backref='blacklisted_user',
        lazy='dynamic'
    )
    
    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
    
    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
    
    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None
    
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None
    
    def block(self, user):
        if not self.is_blocking(user):
            blacklist = Blacklist(user_id=self.id, blacklisted_user_id=user.id)
            db.session.add(blacklist)
    
    def unblock(self, user):
        blacklist = self.blacklisted.filter_by(blacklisted_user_id=user.id).first()
        if blacklist:
            db.session.delete(blacklist)
    
    def is_blocking(self, user):
        return self.blacklisted.filter_by(blacklisted_user_id=user.id).first() is not None
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.following.count()
    
    @property
    def posts_count(self):
        return self.posts.count()
    
    @property
    def likes_count(self):
        return Like.query.filter_by(user_id=self.id).count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'avatar': self.avatar or 'https://picsum.photos/200/200?random=' + str(self.id),
            'bio': self.bio or '',
            'gender': self.gender,
            'birthday': self.birthday,
            'location': self.location or '',
            'is_verified': self.is_verified,
            'verified_type': self.verified_type,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'posts_count': self.posts_count,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat() + 'Z'
        }

class Follow(db.Model):
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='_follower_followed_uc'),
    )

class Blacklist(db.Model):
    __tablename__ = 'blacklists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    blacklisted_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(255))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'blacklisted_user_id', name='_user_blacklisted_uc'),
    )

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text)  # JSON string of image URLs
    topic = db.Column(db.String(100))
    location = db.Column(db.String(100))
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    @property
    def shares_count(self):
        return 0  # TODO: Implement share functionality
    
    def is_liked_by(self, user):
        if user is None:
            return False
        return self.likes.filter_by(user_id=user.id).first() is not None
    
    def to_dict(self, current_user=None):
        import json
        images_list = json.loads(self.images) if self.images else []
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.author.nickname or self.author.username,
            'user_avatar': self.author.avatar or 'https://picsum.photos/200/200?random=' + str(self.author.id),
            'content': self.content,
            'images': images_list,
            'topic': self.topic or '',
            'location': self.location or '',
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'created_at': self.created_at.isoformat() + 'Z',
            'is_liked': self.is_liked_by(current_user)
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.author.nickname or self.author.username,
            'user_avatar': self.author.avatar or 'https://picsum.photos/200/200?random=' + str(self.author.id),
            'post_id': self.post_id,
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() + 'Z'
        }

class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='_user_post_like_uc'),
    )

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    posts_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'posts_count': self.posts_count,
            'created_at': self.created_at.isoformat() + 'Z'
        }
