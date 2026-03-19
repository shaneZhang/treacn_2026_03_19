from flask import Blueprint, jsonify, request
from app.models.mock_data import news_list

news_bp = Blueprint('news', __name__)

@news_bp.route('/api/news', methods=['GET'])
def get_news_list():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    news_type = request.args.get('type', 'all')
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "news": news_list,
            "total": len(news_list),
            "page": page,
            "page_size": page_size,
            "has_more": len(news_list) > page * page_size
        }
    })

@news_bp.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    news_item = next((n for n in news_list if n["id"] == news_id), None)
    
    if news_item:
        return jsonify({
            "code": 200,
            "message": "success",
            "data": news_item
        })
    else:
        return jsonify({
            "code": 404,
            "message": "新闻不存在",
            "data": None
        })
