import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        创建普通用户
        可以是微信小程序用户（username为openid）或管理员（username为邮箱/用户名）
        """
        if not username:
            raise ValueError('用户必须提供一个用户名')
        
        # 如果是邮箱格式，则标准化邮箱
        if email:
            email = self.normalize_email(email)
        
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        创建超级用户（管理员）
        使用传统的用户名/邮箱 + 密码方式
        """
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('login_type', 'password')
        
        if not password:
            raise ValueError('超级用户必须设置密码')
        
        return self.create_user(username, email, password, **extra_fields)
    
    def create_wechat_user(self, wechat_openid, wechat_unionid=None, **extra_fields):
        """
        创建微信小程序用户
        """
        extra_fields.setdefault('role', 'user')
        extra_fields.setdefault('login_type', 'wechat')
        
        user = self.model(
            username=wechat_openid,  # 使用openid作为用户名
            wechat_openid=wechat_openid,
            wechat_unionid=wechat_unionid,
            **extra_fields
        )
        
        # 微信小程序用户不需要密码
        user.set_unusable_password()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """用户模型"""
    
    LOGIN_TYPE_CHOICES = (
        ('password', '账号密码登录'),
        ('wechat', '微信小程序登录'),
    )
    
    ROLE_CHOICES = (
        ('user', '普通用户'),
        ('admin', '管理员'),
    )
    
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 基础认证字段
    username = models.CharField(max_length=150, unique=True, verbose_name='用户名')
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name='邮箱地址')
    
    # 登录类型和角色
    login_type = models.CharField(max_length=20, choices=LOGIN_TYPE_CHOICES, default='password', verbose_name='登录方式')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='角色')
    
    # 微信小程序相关字段
    wechat_openid = models.CharField(max_length=64, unique=True, blank=True, null=True, verbose_name='微信OpenID')
    wechat_unionid = models.CharField(max_length=64, unique=True, blank=True, null=True, verbose_name='微信UnionID')
    
    # Django用户系统必需字段
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_staff = models.BooleanField(default=False, verbose_name='是否为员工')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='加入时间')
    
    # 使用username作为认证字段，更灵活
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # 创建超级用户时不需要额外字段
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        # 添加数据库约束，确保数据完整性
        constraints = [
            models.CheckConstraint(
                check=models.Q(login_type='wechat', wechat_openid__isnull=False) | 
                      models.Q(login_type='password', wechat_openid__isnull=True),
                name='wechat_user_must_have_openid'
            ),
        ]
    
    def __str__(self):
        if self.login_type == 'wechat':
            return f"微信用户({self.wechat_openid[:8]}...)"
        elif self.email:
            return f"{self.email} ({self.role})"
        else:
            return f"{self.username} ({self.role})"
    
    def clean(self):
        """
        模型验证：微信小程序用户必须有openid
        """
        super().clean()
        if self.login_type == 'wechat' and not self.wechat_openid:
            raise ValueError('微信小程序用户必须提供openid')
    
    @property
    def is_wechat_user(self):
        """是否为微信小程序用户"""
        return self.login_type == 'wechat'
    
    @property
    def is_password_user(self):
        """是否为账号密码用户"""
        return self.login_type == 'password'


class UserProfile(models.Model):
    """用户资料扩展模型"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    nickname = models.CharField(max_length=64, verbose_name='昵称', blank=True, default='')
    avatar = models.URLField(max_length=500, verbose_name='头像URL', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=User.GENDER_CHOICES, verbose_name='性别', blank=True, null=True)
    birthday = models.DateField(verbose_name='生日', blank=True, null=True)
    bio = models.TextField(verbose_name='个人简介', blank=True, default='')
    
    # 联系信息
    phone = models.CharField(max_length=20, verbose_name='手机号', blank=True, null=True)
    address = models.CharField(max_length=200, verbose_name='地址', blank=True, default='')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f"{self.nickname or self.user.username} 的资料"