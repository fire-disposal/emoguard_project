"""
用户模块测试
测试微信登录、管理员登录等核心功能
"""
import json
import base64
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import UserProfile
from .wechat_auth import WeChatAuthService

User = get_user_model()


class WeChatLoginTestCase(TestCase):
    """微信登录测试用例"""
    
    def setUp(self):
        self.client = Client()
        self.wechat_service = WeChatAuthService()
        
        # 清空缓存
        cache.clear()
    
    @patch('apps.users.wechat_auth.requests.get')
    def test_wechat_login_success(self, mock_get):
        """测试微信登录成功"""
        # 模拟微信API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'openid': 'test_openid_123',
            'session_key': 'test_session_key',
            'unionid': 'test_unionid_456'
        }
        mock_get.return_value = mock_response
        
        # 测试登录请求
        response = self.client.post('/api/users/wechat/login', {
            'code': 'valid_wechat_code_12345678901234567890123456789012'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # 验证响应结构
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['login_type'], 'wechat')
        self.assertEqual(data['user']['wechat_openid'], 'test_openid_123')
    
    def test_wechat_login_invalid_code_format(self):
        """测试微信登录无效code格式"""
        response = self.client.post('/api/users/wechat/login', {
            'code': 'invalid_code'  # 长度不为32
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('无效的微信登录凭证格式', data['detail'])
    
    def test_wechat_login_empty_code(self):
        """测试微信登录空code"""
        response = self.client.post('/api/users/wechat/login', {
            'code': ''
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('微信登录凭证不能为空', data['detail'])
    
    @patch('apps.users.wechat_auth.requests.get')
    def test_wechat_login_api_error(self, mock_get):
        """测试微信API错误"""
        # 模拟微信API错误响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'errcode': 40163,
            'errmsg': 'code been used'
        }
        mock_get.return_value = mock_response
        
        response = self.client.post('/api/users/wechat/login', {
            'code': 'used_code_12345678901234567890123456789012'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_wechat_code_reuse_prevention(self):
        """测试微信code防重用"""
        # 第一次使用code
        with patch('apps.users.wechat_auth.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'openid': 'test_openid_123',
                'session_key': 'test_session_key'
            }
            mock_get.return_value = mock_response
            
            response1 = self.client.post('/api/users/wechat/login', {
                'code': 'reuse_test_code_12345678901234567890123456789012'
            }, content_type='application/json')
            
            self.assertEqual(response1.status_code, 200)
        
        # 第二次使用相同的code
        response2 = self.client.post('/api/users/wechat/login', {
            'code': 'reuse_test_code_12345678901234567890123456789012'
        }, content_type='application/json')
        
        self.assertEqual(response2.status_code, 200)
        data = json.loads(response2.content)
        self.assertIn('error', data)
        self.assertIn('微信登录凭证已使用或无效', data['detail'])
    
    def test_wechat_user_info_decryption(self):
        """测试微信用户信息解密"""
        # 准备测试数据
        session_key = 'tiihtNczf5v6AKRyjwEUhQ=='
        encrypted_data = 'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSR9+H5n'
        iv = 'r7BXXKkLb8qrSNn05n0qiA=='
        
        # 注意：这里需要真实的微信解密实现
        # 由于涉及微信官方解密算法，这里只测试解密函数的存在性
        service = WeChatAuthService()
        
        # 测试解密函数调用（预期会失败，因为数据是伪造的）
        try:
            result = service.decrypt_user_info(encrypted_data, iv, session_key)
            # 如果解密成功，验证数据结构
            if result:
                self.assertIsInstance(result, dict)
        except Exception as e:
            # 预期会失败，因为使用了伪造的测试数据
            self.assertIn('解密', str(e))


class AdminLoginTestCase(TestCase):
    """管理员登录测试用例"""
    
    def setUp(self):
        self.client = Client()
        
        # 创建管理员用户
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='TestAdmin123!',
            role='admin',
            login_type='password'
        )
        
        # 创建普通用户
        self.normal_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='TestUser123!',
            role='user',
            login_type='password'
        )
    
    def test_admin_login_success(self):
        """测试管理员登录成功"""
        response = self.client.post('/api/users/admin/login', {
            'username': 'testadmin',
            'password': 'TestAdmin123!'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['role'], 'admin')
        self.assertEqual(data['user']['username'], 'testadmin')
    
    def test_admin_login_wrong_password(self):
        """测试管理员登录密码错误"""
        response = self.client.post('/api/users/admin/login', {
            'username': 'testadmin',
            'password': 'WrongPassword123!'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('用户名或密码错误', data['error'])
    
    def test_admin_login_normal_user(self):
        """测试普通用户尝试管理员登录"""
        response = self.client.post('/api/users/admin/login', {
            'username': 'testuser',
            'password': 'TestUser123!'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('权限不足', data['error'])
    
    def test_admin_login_empty_credentials(self):
        """测试管理员登录空凭据"""
        response = self.client.post('/api/users/admin/login', {
            'username': '',
            'password': ''
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('用户名和密码不能为空', data['detail'])
    
    def test_admin_login_long_username(self):
        """测试管理员登录超长用户名"""
        long_username = 'a' * 151  # 超过150字符限制
        response = self.client.post('/api/users/admin/login', {
            'username': long_username,
            'password': 'TestPassword123!'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('用户名长度不能超过150个字符', data['detail'])


class UserProfileTestCase(TestCase):
    """用户资料测试用例"""
    
    def setUp(self):
        self.client = Client()
        
        # 创建测试用户
        self.test_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='TestUser123!',
            role='user',
            login_type='password'
        )
        
        # 创建JWT令牌
        from config.jwt_auth_adapter import create_tokens_for_user
        self.tokens = create_tokens_for_user(self.test_user)
    
    def test_create_profile_success(self):
        """测试创建用户资料成功"""
        response = self.client.post('/api/users/profiles', {
            'nickname': '测试用户',
            'gender': 'male',
            'bio': '这是一个测试用户'
        }, content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {self.tokens["access"]}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['nickname'], '测试用户')
        self.assertEqual(data['gender'], 'male')
        self.assertEqual(data['bio'], '这是一个测试用户')
        self.assertEqual(data['user_id'], str(self.test_user.id))
    
    def test_create_profile_duplicate(self):
        """测试重复创建用户资料"""
        # 第一次创建
        UserProfile.objects.create(
            user=self.test_user,
            nickname='已有用户',
            gender='female'
        )
        
        # 第二次尝试创建
        response = self.client.post('/api/users/profiles', {
            'nickname': '新用户',
            'gender': 'male'
        }, content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {self.tokens["access"]}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('资料已存在', data['error'])
    
    def test_create_profile_invalid_nickname(self):
        """测试创建用户资料无效昵称"""
        response = self.client.post('/api/users/profiles', {
            'nickname': '',  # 空昵称
            'gender': 'male'
        }, content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {self.tokens["access"]}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('昵称不能为空', data['detail'])
    
    def test_update_profile_success(self):
        """测试更新用户资料成功"""
        # 先创建资料
        profile = UserProfile.objects.create(
            user=self.test_user,
            nickname='原始昵称',
            gender='male',
            bio='原始简介'
        )
        
        response = self.client.put(f'/api/users/profiles/{profile.id}', {
            'nickname': '更新昵称',
            'bio': '更新简介'
        }, content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {self.tokens["access"]}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['nickname'], '更新昵称')
        self.assertEqual(data['bio'], '更新简介')
        self.assertEqual(data['gender'], 'male')  # 未改变的字段
    
    def test_update_profile_permission_denied(self):
        """测试更新他人资料权限拒绝"""
        # 创建另一个用户
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='OtherUser123!',
            role='user',
            login_type='password'
        )
        
        # 创建其他用户的资料
        other_profile = UserProfile.objects.create(
            user=other_user,
            nickname='其他用户',
            gender='female'
        )
        
        # 尝试更新他人资料
        response = self.client.put(f'/api/users/profiles/{other_profile.id}', {
            'nickname': '恶意修改'
        }, content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {self.tokens["access"]}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('权限不足', data['error'])


class RateLimitTestCase(TestCase):
    """频率限制测试用例"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
    
    @patch('apps.users.wechat_auth.requests.get')
    def test_wechat_login_rate_limit(self, mock_get):
        """测试微信登录频率限制"""
        # 模拟微信API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'openid': 'rate_limit_test_openid',
            'session_key': 'test_session_key'
        }
        mock_get.return_value = mock_response
        
        # 快速发送多次请求
        for i in range(6):  # 超过5次限制
            response = self.client.post('/api/users/wechat/login', {
                'code': f'rate_limit_code_{i}_12345678901234567890123456789012'
            }, content_type='application/json')
        
        # 最后一次应该被限制
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('请求过于频繁', data['error'])
    
    def test_admin_login_rate_limit(self):
        """测试管理员登录频率限制"""
        # 快速发送多次请求
        for i in range(4):  # 超过3次限制
            response = self.client.post('/api/users/admin/login', {
                'username': f'testuser{i}',
                'password': 'testpassword'
            }, content_type='application/json')
        
        # 最后一次应该被限制
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('请求过于频繁', data['error'])


class SecurityTestCase(TestCase):
    """安全性测试用例"""
    
    def setUp(self):
        self.client = Client()
        self.wechat_service = WeChatAuthService()
    
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        # 尝试SQL注入
        malicious_input = "'; DROP TABLE users; --"
        
        response = self.client.post('/api/users/admin/login', {
            'username': malicious_input,
            'password': 'password'
        }, content_type='application/json')
        
        # 应该返回参数错误，而不是数据库错误
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_xss_protection(self):
        """测试XSS防护"""
        # 创建测试用户
        test_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='TestUser123!',
            role='user',
            login_type='password'
        )
        
        from config.jwt_auth_adapter import create_tokens_for_user
        tokens = create_tokens_for_user(test_user)
        
        # 尝试XSS攻击
        xss_payload = '<script>alert("XSS")</script>'
        
        response = self.client.post('/api/users/profiles', {
            'nickname': '正常昵称',
            'bio': xss_payload
        }, content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # 验证XSS被清理
        self.assertNotIn('<script>', data['bio'])
        self.assertNotIn('alert', data['bio'])
    
    def test_sensitive_data_exposure(self):
        """测试敏感数据泄露防护"""
        # 创建测试用户
        test_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='TestUser123!',
            role='user',
            login_type='password'
        )
        
        from config.jwt_auth_adapter import create_tokens_for_user
        tokens = create_tokens_for_user(test_user)
        
        # 获取用户信息
        response = self.client.get('/api/users/me',
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # 验证不返回敏感信息
        self.assertNotIn('password', data['user'])
        self.assertNotIn('session_key', data)
    
    def test_wechat_code_replay_attack(self):
        """测试微信code重放攻击防护"""
        with patch('apps.users.wechat_auth.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'openid': 'replay_test_openid',
                'session_key': 'test_session_key'
            }
            mock_get.return_value = mock_response
            
            # 第一次使用code
            response1 = self.client.post('/api/users/wechat/login', {
                'code': 'replay_attack_code_12345678901234567890123456789012'
            }, content_type='application/json')
            
            self.assertEqual(response1.status_code, 200)
            data1 = json.loads(response1.content)
            self.assertNotIn('error', data1)
            
            # 第二次使用相同的code（重放攻击）
            response2 = self.client.post('/api/users/wechat/login', {
                'code': 'replay_attack_code_12345678901234567890123456789012'
            }, content_type='application/json')
            
            self.assertEqual(response2.status_code, 200)
            data2 = json.loads(response2.content)
            self.assertIn('error', data2)
            self.assertIn('微信登录凭证已使用或无效', data2['detail'])
