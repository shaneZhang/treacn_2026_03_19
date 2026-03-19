#!/usr/bin/env python3
"""
批量修复JWT identity问题
将所有 User.query.get(current_user_id) 替换为 User.query.get(int(current_user_id))
"""

import os
import re

routes_dir = '/Users/zhangyuqing/Desktop/trae_2026_03_19/interest_social_api/app/routes'

# 要替换的模式
patterns = [
    # User.query.get(current_user_id) -> User.query.get(int(current_user_id))
    (r'User\.query\.get\(current_user_id\)', r'User.query.get(int(current_user_id))'),
    # current_user_id == user_id (比较时需要转int)
    (r'current_user_id == user_id', r'int(current_user_id) == user_id'),
    # user_id=current_user_id (数据库查询参数)
    (r'user_id=current_user_id', r'user_id=int(current_user_id)'),
    # follower_id=current_user_id
    (r'follower_id=current_user_id', r'follower_id=int(current_user_id)'),
    # blocking_id=current_user_id
    (r'blocking_id=current_user_id', r'blocking_id=int(current_user_id)'),
    # Post.query.get
    (r'Post\.query\.get\(current_user_id\)', r'Post.query.get(int(current_user_id))'),
    # Comment.query.get
    (r'Comment\.query\.get\(current_user_id\)', r'Comment.query.get(int(current_user_id))'),
]

for filename in os.listdir(routes_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(routes_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'已修复: {filename}')
        else:
            print(f'无需修改: {filename}')

print('修复完成!')
