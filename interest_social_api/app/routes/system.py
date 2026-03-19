from flask import Blueprint, jsonify, request
from app.models.mock_data import app_version

system_bp = Blueprint('system', __name__)

@system_bp.route('/api/system/check-update', methods=['GET'])
def check_update():
    current_version = request.args.get('version', '1.0.0')
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "has_update": True,
            "latest_version": app_version["latest_version"],
            "min_supported_version": app_version["min_supported_version"],
            "update_content": app_version["update_content"],
            "download_url": app_version["download_url"],
            "force_update": app_version["force_update"],
            "release_date": app_version["release_date"]
        }
    })
