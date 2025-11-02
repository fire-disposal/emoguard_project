"""
用户模块测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """用户模型测试"""
    
    def test_create_user(self):
        """测试创建用户"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.role, 'user')
        self.assertEqual(user.login_type, 'password')
    
    def test_create_wechat_user(self):
        """测试创建微信用户"""
        user = User.objects.create_wechat_user(
            wechat_openid='test_openid_123',
            wechat_unionid='test_unionid_123'
        )
        self.assertEqual(user.username, 'test_openid_123')
        self.assertEqual(user.wechat_openid, 'test_openid_123')
        self.assertEqual(user.wechat_unionid, 'test_unionid_123')
        self.assertEqual(user.login_type, 'wechat')
        self.assertFalse(user.has_usable_password())
    
    def test_create_superuser(self):
        """测试创建超级用户"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.assertEqual(admin.role, 'admin')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)


class UserProfileTest(TestCase):
    """用户资料测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_profile(self):
        """测试创建用户资料"""
        profile = UserProfile.objects.create(
            user=self.user,
            nickname='测试用户',
            gender='male',
            bio='这是一个测试用户'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.nickname, '测试用户')
        self.assertEqual(profile.gender, 'male')
        self.assertEqual(profile.bio, '这是一个测试用户')
    
    def test_profile_str(self):
        """测试用户资料字符串表示"""
        profile = UserProfile.objects.create(
            user=self.user,
            nickname='测试用户'
        )
        self.assertEqual(str(profile), '测试用户 的资料')
        
        # 测试没有昵称的情况
        profile.nickname = ''
        profile.save()
        self.assertEqual(str(profile), 'testuser 的资料')
