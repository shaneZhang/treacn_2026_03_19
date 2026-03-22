import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.auth.jwt_handler import jwt_handler
from app.auth.crypto import password_handler, encryption_handler, api_key_handler


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


class TestHealthEndpoints:
    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_ready_check(self, client):
        response = client.get('/ready')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ready'


class TestAPIEndpoints:
    def test_index(self, client):
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
        assert 'endpoints' in data['data']

    def test_home(self, client):
        response = client.get('/api/home')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200

    def test_profile(self, client):
        response = client.get('/api/profile')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200

    def test_news_list(self, client):
        response = client.get('/api/news')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200

    def test_system_check_update(self, client):
        response = client.get('/api/system/check-update')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200


class TestAuthEndpoints:
    def test_register_missing_data(self, client):
        response = client.post('/api/auth/register', 
                              json={},
                              content_type='application/json')
        assert response.status_code == 400

    def test_register_success(self, client):
        response = client.post('/api/auth/register',
                              json={
                                  'username': 'testuser',
                                  'email': 'test@example.com',
                                  'password': 'TestPass123!'
                              },
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200

    def test_login_missing_data(self, client):
        response = client.post('/api/auth/login',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400

    def test_login_success(self, client):
        response = client.post('/api/auth/login',
                              json={
                                  'username': 'testuser',
                                  'password': 'TestPass123!'
                              },
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']


class TestJWTHandler:
    def test_generate_access_token(self):
        token = jwt_handler.generate_access_token(user_id=1)
        assert token is not None
        assert isinstance(token, str)

    def test_generate_refresh_token(self):
        token = jwt_handler.generate_refresh_token(user_id=1)
        assert token is not None
        assert isinstance(token, str)

    def test_verify_access_token(self):
        token = jwt_handler.generate_access_token(user_id=1)
        result = jwt_handler.verify_access_token(token)
        assert result['valid'] is True
        assert result['payload']['sub'] == '1'

    def test_verify_invalid_token(self):
        result = jwt_handler.verify_access_token('invalid_token')
        assert result['valid'] is False


class TestPasswordHandler:
    def test_hash_password(self):
        password = 'TestPassword123!'
        password_hash, salt = password_handler.hash_password(password)
        assert password_hash is not None
        assert salt is not None
        assert len(salt) == 32

    def test_verify_password(self):
        password = 'TestPassword123!'
        password_hash, salt = password_handler.hash_password(password)
        assert password_handler.verify_password(password, password_hash, salt) is True
        assert password_handler.verify_password('WrongPassword', password_hash, salt) is False


class TestEncryptionHandler:
    def test_encrypt_decrypt(self):
        data = 'sensitive_data_123'
        encrypted = encryption_handler.encrypt(data)
        assert encrypted != data
        decrypted = encryption_handler.decrypt(encrypted)
        assert decrypted == data


class TestAPIKeyHandler:
    def test_generate_api_key(self):
        api_key, key_hash = api_key_handler.generate_api_key()
        assert api_key.startswith('isk_')
        assert key_hash is not None

    def test_verify_api_key(self):
        api_key, key_hash = api_key_handler.generate_api_key()
        assert api_key_handler.verify_api_key(api_key, key_hash) is True
        assert api_key_handler.verify_api_key('isk_invalid', key_hash) is False


class TestSecurityMiddleware:
    def test_sql_injection_detection(self):
        from app.middleware.security import SecurityMiddleware
        
        assert SecurityMiddleware.detect_sql_injection("SELECT * FROM users") is True
        assert SecurityMiddleware.detect_sql_injection("normal text") is False

    def test_xss_detection(self):
        from app.middleware.security import SecurityMiddleware
        
        assert SecurityMiddleware.detect_xss("<script>alert('xss')</script>") is True
        assert SecurityMiddleware.detect_xss("normal text") is False


class TestRateLimiting:
    def test_rate_limit_headers(self, client):
        response = client.get('/')
        assert 'X-RateLimit-Limit' in response.headers


class TestSecurityHeaders:
    def test_security_headers_present(self, client):
        response = client.get('/')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
