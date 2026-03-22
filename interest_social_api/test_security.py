#!/usr/bin/env python3
"""安全功能测试脚本"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_login():
    """测试登录功能"""
    print("=" * 50)
    print("测试登录功能")
    print("=" * 50)
    
    login_data = {
        "username": "user1",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        return response.json()['data']['access_token']
    return None

def test_protected_route(access_token):
    """测试受保护路由"""
    print("\n" + "=" * 50)
    print("测试受保护路由（带有效token）")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}/api/home", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

def test_protected_route_without_token():
    """测试无token访问受保护路由"""
    print("\n" + "=" * 50)
    print("测试受保护路由（无token）")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/home")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

def test_sql_injection_attack():
    """测试SQL注入防护"""
    print("\n" + "=" * 50)
    print("测试SQL注入防护")
    print("=" * 50)
    
    # 尝试SQL注入
    malicious_data = {
        "username": "admin' OR '1'='1",
        "password": "any"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=malicious_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

def test_xss_attack():
    """测试XSS防护"""
    print("\n" + "=" * 50)
    print("测试XSS防护（注册带脚本的用户名）")
    print("=" * 50)
    
    xss_data = {
        "username": "<script>alert('xss')</script>",
        "password": "test123",
        "email": "xss@test.com"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=xss_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

def test_invalid_token():
    """测试无效token"""
    print("\n" + "=" * 50)
    print("测试无效token")
    print("=" * 50)
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.get(f"{BASE_URL}/api/home", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

def test_refresh_token():
    """测试刷新token"""
    print("\n" + "=" * 50)
    print("测试获取refresh token")
    print("=" * 50)
    
    login_data = {
        "username": "user1",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        refresh_token = response.json()['data']['refresh_token']
        print(f"Refresh Token获取成功")
        
        # 使用refresh token获取新的access token
        print("\n测试使用refresh token刷新access token")
        headers = {
            "Authorization": f"Bearer {refresh_token}"
        }
        refresh_response = requests.post(f"{BASE_URL}/api/auth/refresh", headers=headers)
        print(f"状态码: {refresh_response.status_code}")
        print(f"响应: {json.dumps(refresh_response.json(), ensure_ascii=False, indent=2)}")

def test_security_headers():
    """测试安全头"""
    print("\n" + "=" * 50)
    print("测试安全头")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/")
    print("响应头:")
    for header, value in response.headers.items():
        if header.lower() in ['x-frame-options', 'x-xss-protection', 'x-content-type-options', 
                              'content-security-policy', 'referrer-policy', 'server']:
            print(f"  {header}: {value}")

if __name__ == "__main__":
    print("安全功能测试套件")
    print("=" * 70)
    
    # 测试安全头
    test_security_headers()
    
    # 测试无token访问
    test_protected_route_without_token()
    
    # 测试登录
    access_token = test_login()
    
    if access_token:
        # 测试受保护路由
        test_protected_route(access_token)
        
        # 测试刷新token
        test_refresh_token()
    
    # 测试无效token
    test_invalid_token()
    
    # 测试SQL注入防护
    test_sql_injection_attack()
    
    # 测试XSS防护
    test_xss_attack()
    
    print("\n" + "=" * 70)
    print("测试完成!")