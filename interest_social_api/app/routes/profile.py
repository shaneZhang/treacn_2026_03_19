from flask import Blueprint, jsonify
from app.models.mock_data import (
    current_user, user_posts, user_followers, 
    user_following, user_liked_posts
)

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "user": current_user,
            "stats": {
                "posts_count": current_user["posts_count"],
                "followers_count": current_user["followers_count"],
                "following_count": current_user["following_count"],
                "likes_count": current_user["likes_count"]
            }
        }
    })

@profile_bp.route('/api/profile/posts', methods=['GET'])
def get_user_posts():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "posts": user_posts,
            "total": len(user_posts),
            "page": 1,
            "page_size": 20
        }
    })

@profile_bp.route('/api/profile/followers', methods=['GET'])
def get_followers():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "followers": user_followers,
            "total": len(user_followers),
            "has_more": True
        }
    })

@profile_bp.route('/api/profile/following', methods=['GET'])
def get_following():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "following": user_following,
            "total": len(user_following),
            "has_more": False
        }
    })

@profile_bp.route('/api/profile/liked', methods=['GET'])
def get_liked_posts():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "posts": user_liked_posts,
            "total": len(user_liked_posts),
            "page": 1,
            "page_size": 20
        }
    })
