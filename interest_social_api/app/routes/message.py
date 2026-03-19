from flask import Blueprint, jsonify, request
from app.models.mock_data import (
    notifications, conversation_list, private_messages, current_user
)
import time

message_bp = Blueprint('message', __name__)

@message_bp.route('/api/messages/notifications', methods=['GET'])
def get_notifications():
    unread_count = sum(1 for n in notifications if not n["is_read"])
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "notifications": notifications,
            "unread_count": unread_count,
            "total": len(notifications)
        }
    })

@message_bp.route('/api/messages/conversations', methods=['GET'])
def get_conversations():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "conversations": conversation_list,
            "total": len(conversation_list),
            "total_unread": sum(c["unread_count"] for c in conversation_list)
        }
    })

@message_bp.route('/api/messages/private/<int:user_id>', methods=['GET'])
def get_private_messages(user_id):
    messages = [m for m in private_messages if 
                (m["from_user_id"] == user_id and m["to_user_id"] == current_user["id"]) or
                (m["from_user_id"] == current_user["id"] and m["to_user_id"] == user_id)]
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "messages": sorted(messages, key=lambda x: x["created_at"]),
            "total": len(messages)
        }
    })

@message_bp.route('/api/messages/send', methods=['POST'])
def send_private_message():
    data = request.get_json()
    to_user_id = data.get('to_user_id')
    content = data.get('content')
    
    new_message = {
        "id": int(time.time() * 1000),
        "from_user_id": current_user["id"],
        "from_user_nickname": current_user["nickname"],
        "from_user_avatar": current_user["avatar"],
        "to_user_id": to_user_id,
        "content": content,
        "is_read": False,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    return jsonify({
        "code": 200,
        "message": "发送成功",
        "data": {
            "message": new_message
        }
    })

@message_bp.route('/api/messages/read/<int:conversation_id>', methods=['POST'])
def mark_as_read(conversation_id):
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "is_read": True
        }
    })

@message_bp.route('/api/messages/check-read/<int:user_id>', methods=['GET'])
def check_message_read(user_id):
    unread_messages = [m for m in private_messages 
                      if m["from_user_id"] == user_id and not m["is_read"]]
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "user_id": user_id,
            "has_unread": len(unread_messages) > 0,
            "unread_count": len(unread_messages)
        }
    })

@message_bp.route('/api/messages/notification/read-all', methods=['POST'])
def mark_notifications_read():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "updated_count": sum(1 for n in notifications if not n["is_read"])
        }
    })
