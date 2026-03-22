#!/usr/bin/env python3
"""完整功能测试脚本"""

import sys

def test_imports():
    """测试模块导入"""
    try:
        from app import create_app
        from app.utils.security import (
            sanitize_input, detect_sql_injection,
            hash_password, verify_password,
            encrypt_sensitive_data, decrypt_sensitive_data
        )
        print("✓ 模块导入测试: PASSED")
        return create_app, sanitize_input, detect_sql_injection, hash_password, verify_password, encrypt_sensitive_data, decrypt_sensitive_data
    except Exception as e:
        print(f"✗ 模块导入测试: FAILED - {e}")
        sys.exit(1)

def test_xss_protection(sanitize_input):
    """测试XSS防护"""
    try:
        malicious_xss = '<script>alert(1)</script>'
        sanitized = sanitize_input(malicious_xss)
        if '<script>' not in sanitized:
            print("✓ XSS防护测试: PASSED")
            return True
        else:
            print("✗ XSS防护测试: FAILED")
            return False
    except Exception as e:
        print(f"✗ XSS防护测试: FAILED - {e}")
        return False

def test_sql_injection_detection(detect_sql_injection):
    """测试SQL注入检测"""
    try:
        malicious_sql = "' OR '1'='1"
        if detect_sql_injection(malicious_sql) == True:
            if detect_sql_injection('normal_input') == False:
                print("✓ SQL注入检测测试: PASSED")
                return True
        print("✗ SQL注入检测测试: FAILED")
        return False
    except Exception as e:
        print(f"✗ SQL注入检测测试: FAILED - {e}")
        return False

def test_password_hashing(hash_password, verify_password):
    """测试密码哈希"""
    try:
        password = 'test_password_123'
        hashed = hash_password(password)
        if verify_password(hashed, password) == True:
            if verify_password(hashed, 'wrong_password') == False:
                print("✓ 密码哈希测试: PASSED")
                return True
        print("✗ 密码哈希测试: FAILED")
        return False
    except Exception as e:
        print(f"✗ 密码哈希测试: FAILED - {e}")
        return False

def test_encryption(encrypt_sensitive_data, decrypt_sensitive_data):
    """测试加解密功能"""
    try:
        original = 'sensitive_data_12345'
        encrypted = encrypt_sensitive_data(original)
        decrypted = decrypt_sensitive_data(encrypted)
        if decrypted == original:
            print("✓ 敏感数据加密测试: PASSED")
            return True
        print(f"✗ 敏感数据加密测试: FAILED - expected {original}, got {decrypted}")
        return False
    except Exception as e:
        print(f"✗ 敏感数据加密测试: FAILED - {e}")
        return False

def test_flask_app(create_app):
    """测试Flask应用"""
    try:
        app = create_app()
        client = app.test_client()
        
        # 测试未认证访问
        response = client.get('/api/home')
        if response.status_code == 401:
            print("✓ JWT认证拦截测试: PASSED")
        else:
            print(f"✗ JWT认证拦截测试: FAILED - status code {response.status_code}")
            return False
        
        # 测试登录
        response = client.post('/api/auth/login', json={'username': 'user1', 'password': 'password123'})
        if response.status_code == 200:
            data = response.get_json()
            if 'access_token' in data['data']:
                print("✓ 用户登录测试: PASSED")
                token = data['data']['access_token']
            else:
                print("✗ 用户登录测试: FAILED - 缺少access_token")
                return False
        else:
            print(f"✗ 用户登录测试: FAILED - status code {response.status_code}")
            return False
        
        # 测试认证访问
        response = client.get('/api/home', headers={'Authorization': f'Bearer {token}'})
        if response.status_code == 200:
            print("✓ 认证访问测试: PASSED")
        else:
            print(f"✗ 认证访问测试: FAILED - status code {response.status_code}")
            return False
        
        # 测试安全头
        response = client.get('/')
        security_headers = ['X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options', 'Content-Security-Policy']
        headers_present = True
        for header in security_headers:
            if header not in response.headers:
                print(f"✗ 缺少安全头: {header}")
                headers_present = False
        if headers_present:
            print("✓ 安全头设置测试: PASSED")
        
        return True
    except Exception as e:
        print(f"✗ Flask应用测试: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Interest Social API - 完整功能测试")
    print("=" * 60)
    print()
    
    # 运行所有测试
    modules = test_imports()
    if not modules:
        sys.exit(1)
    
    create_app, sanitize_input, detect_sql_injection, hash_password, verify_password, encrypt_sensitive_data, decrypt_sensitive_data = modules
    
    all_passed = True
    all_passed &= test_xss_protection(sanitize_input)
    all_passed &= test_sql_injection_detection(detect_sql_injection)
    all_passed &= test_password_hashing(hash_password, verify_password)
    all_passed &= test_encryption(encrypt_sensitive_data, decrypt_sensitive_data)
    all_passed &= test_flask_app(create_app)
    
    print()
    print("=" * 60)
    if all_passed:
        print("所有测试通过！系统配置正常。")
    else:
        print("部分测试失败，请检查上述错误信息。")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())