#!/usr/bin/env python3
"""
API 测试脚本
用于测试兴趣社交API的各个接口功能
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5001'

# 全局变量存储测试用户信息
test_user = {
    'username': 'testuser_' + str(int(time.time())),
    'email': f'testuser_{int(time.time())}@example.com',
    'password': 'testpassword123',
    'nickname': '测试用户'
}

second_user = {
    'username': 'seconduser_' + str(int(time.time())),
    'email': f'seconduser_{int(time.time())}@example.com',
    'password': 'password456',
    'nickname': '第二个用户'
}

# 存储token
access_token = None
refresh_token = None
second_access_token = None

# 存储测试数据
test_post_id = None
test_comment_id = None


def print_response(response):
    """打印响应结果"""
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    except:
        print(f"响应内容: {response.text}")
        return None


def test_root():
    """测试根接口"""
    print("\n" + "="*60)
    print("测试: 根接口")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/")
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print("✓ 根接口测试通过")


def test_register():
    """测试用户注册"""
    global access_token, refresh_token
    print("\n" + "="*60)
    print("测试: 用户注册")
    print("="*60)
    
    # 注册第一个用户
    print("\n注册第一个用户:")
    response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
    data = print_response(response)
    assert response.status_code == 201
    assert data['code'] == 200
    access_token = data['data']['access_token']
    refresh_token = data['data']['refresh_token']
    print(f"✓ 用户 {test_user['username']} 注册成功")
    
    # 注册第二个用户
    print("\n注册第二个用户:")
    response = requests.post(f"{BASE_URL}/api/auth/register", json=second_user)
    data = print_response(response)
    assert response.status_code == 201
    assert data['code'] == 200
    global second_access_token
    second_access_token = data['data']['access_token']
    print(f"✓ 用户 {second_user['username']} 注册成功")


def test_login():
    """测试用户登录"""
    global access_token, refresh_token
    print("\n" + "="*60)
    print("测试: 用户登录")
    print("="*60)
    
    login_data = {
        'username': test_user['username'],
        'password': test_user['password']
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    access_token = data['data']['access_token']
    refresh_token = data['data']['refresh_token']
    print("✓ 用户登录成功")


def test_get_user_info():
    """测试获取当前用户信息"""
    print("\n" + "="*60)
    print("测试: 获取当前用户信息")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    assert data['data']['user']['username'] == test_user['username']
    print("✓ 获取用户信息成功")


def test_create_post():
    """测试发布帖子"""
    global test_post_id
    print("\n" + "="*60)
    print("测试: 发布帖子")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    post_data = {
        'content': '这是一条测试帖子，内容很精彩！',
        'images': ['https://picsum.photos/400/400?random=100'],
        'topic': '#测试话题#',
        'location': '北京市朝阳区'
    }
    
    response = requests.post(f"{BASE_URL}/api/posts", json=post_data, headers=headers)
    data = print_response(response)
    assert response.status_code == 201
    assert data['code'] == 200
    test_post_id = data['data']['post']['id']
    print(f"✓ 帖子发布成功，帖子ID: {test_post_id}")


def test_get_posts():
    """测试获取帖子列表"""
    print("\n" + "="*60)
    print("测试: 获取帖子列表")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/posts")
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print(f"✓ 获取帖子列表成功，共 {data['data']['total']} 条帖子")


def test_get_post_detail():
    """测试获取帖子详情"""
    print("\n" + "="*60)
    print("测试: 获取帖子详情")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/posts/{test_post_id}")
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    assert data['data']['post']['id'] == test_post_id
    print("✓ 获取帖子详情成功")


def test_like_post():
    """测试点赞帖子"""
    print("\n" + "="*60)
    print("测试: 点赞帖子")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {second_access_token}'}  # 用第二个用户点赞
    response = requests.post(f"{BASE_URL}/api/posts/{test_post_id}/like", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    assert data['data']['is_liked'] == True
    print("✓ 点赞成功")
    
    # 取消点赞
    print("\n取消点赞:")
    response = requests.post(f"{BASE_URL}/api/posts/{test_post_id}/like", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    assert data['data']['is_liked'] == False
    print("✓ 取消点赞成功")


def test_create_comment():
    """测试发布评论"""
    global test_comment_id
    print("\n" + "="*60)
    print("测试: 发布评论")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {second_access_token}'}
    comment_data = {
        'content': '写得真好，支持一下！'
    }
    
    response = requests.post(
        f"{BASE_URL}/api/posts/{test_post_id}/comments",
        json=comment_data,
        headers=headers
    )
    data = print_response(response)
    assert response.status_code == 201
    assert data['code'] == 200
    test_comment_id = data['data']['comment']['id']
    print(f"✓ 评论发布成功，评论ID: {test_comment_id}")


def test_get_comments():
    """测试获取评论列表"""
    print("\n" + "="*60)
    print("测试: 获取评论列表")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/posts/{test_post_id}/comments")
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print(f"✓ 获取评论列表成功，共 {data['data']['total']} 条评论")


def test_follow_user():
    """测试关注用户"""
    print("\n" + "="*60)
    print("测试: 关注用户")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # 获取第二个用户的ID
    response = requests.get(f"{BASE_URL}/api/auth/me", headers={'Authorization': f'Bearer {second_access_token}'})
    second_user_id = response.json()['data']['user']['id']
    
    # 关注第二个用户
    response = requests.post(f"{BASE_URL}/api/social/follow/{second_user_id}", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    assert data['data']['is_following'] == True
    print("✓ 关注成功")
    
    # 查看关注列表
    response = requests.get(f"{BASE_URL}/api/profile/following", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print("✓ 查看关注列表成功")


def test_block_user():
    """测试拉黑用户"""
    print("\n" + "="*60)
    print("测试: 拉黑用户")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # 获取第二个用户的ID
    response = requests.get(f"{BASE_URL}/api/auth/me", headers={'Authorization': f'Bearer {second_access_token}'})
    second_user_id = response.json()['data']['user']['id']
    
    # 拉黑第二个用户
    response = requests.post(f"{BASE_URL}/api/social/block/{second_user_id}", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print("✓ 拉黑成功")
    
    # 查看黑名单
    response = requests.get(f"{BASE_URL}/api/social/blocklist", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print(f"✓ 黑名单中有 {data['data']['total']} 个用户")


def test_search_users():
    """测试搜索用户"""
    print("\n" + "="*60)
    print("测试: 搜索用户")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/search/users?keyword=test")
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print(f"✓ 搜索到 {data['data']['total']} 个用户")


def test_search_posts():
    """测试搜索帖子"""
    print("\n" + "="*60)
    print("测试: 搜索帖子")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/search/posts?keyword=测试")
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print(f"✓ 搜索到 {data['data']['total']} 条帖子")


def test_search_topics():
    """测试搜索话题"""
    print("\n" + "="*60)
    print("测试: 搜索话题")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/search/topics?keyword=测试")
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print(f"✓ 搜索到 {data['data']['total']} 个话题")


def test_delete_post():
    """测试删除帖子"""
    print("\n" + "="*60)
    print("测试: 删除帖子")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(f"{BASE_URL}/api/posts/{test_post_id}", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print("✓ 帖子删除成功")


def test_logout():
    """测试用户登出"""
    print("\n" + "="*60)
    print("测试: 用户登出")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    data = print_response(response)
    assert response.status_code == 200
    assert data['code'] == 200
    print("✓ 用户登出成功")


def main():
    """运行所有测试"""
    print("开始运行 API 测试...")
    print(f"测试服务器: {BASE_URL}")
    
    try:
        # 基础测试
        test_root()
        test_register()
        test_login()
        test_get_user_info()
        
        # 帖子相关测试
        test_create_post()
        test_get_posts()
        test_get_post_detail()
        test_like_post()
        test_create_comment()
        test_get_comments()
        
        # 社交相关测试
        test_follow_user()
        test_block_user()
        
        # 搜索相关测试
        test_search_users()
        test_search_posts()
        test_search_topics()
        
        # 删除和登出测试
        test_delete_post()
        test_logout()
        
        print("\n" + "="*60)
        print("✓ 所有测试通过!")
        print("="*60)
        
    except AssertionError as e:
        print("\n" + "="*60)
        print("✗ 测试失败!")
        print(f"错误信息: {e}")
        print("="*60)
        raise
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ 发生错误: {e}")
        print("="*60)
        raise


if __name__ == '__main__':
    main()
