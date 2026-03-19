from flask import Blueprint, jsonify
from app.models.mock_data import (
    home_banners, hot_topics, recommended_users, 
    recommended_posts, interest_categories
)

home_bp = Blueprint('home', __name__)

@home_bp.route('/api/home', methods=['GET'])
def get_home_data():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "banners": home_banners,
            "hot_topics": hot_topics,
            "recommended_users": recommended_users,
            "recommended_posts": recommended_posts,
            "interest_categories": interest_categories
        }
    })
