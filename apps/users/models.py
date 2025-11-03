"""用户模型
使用Django推荐的AbstractUser，简单、安全、符合惯例
支持账号密码和微信小程序登录
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    用户模型 - 使用AbstractUser简化设计
    支持两种登录方式：
    1. 账号密码登录（管理员）
    2. 微信小程序登录（普通用户）
    
    AbstractUser已包含：
    - username, email, password
    - first_name, last_name
    - is_active, is_staff, is_superuser
    - date_joined, last_login
    - groups, user_permissions
    """
    
    ROLE_CHOICES = [
        ('user', '普通用户'),
        ('admin', '管理员'),
    ]
    
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]
    
    EDUCATION_CHOICES = [
        ('primary', '小学'),
        ('middle', '初中'),
        ('high', '高中'),
        ('associate', '大专'),
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('doctor', '博士'),
        ('other', '其他'),
    ]
    
    # 使用UUID作为主键（更安全）
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    
    # ========== 微信字段 ==========
    wechat_openid = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        null=True,
        verbose_name='微信OpenID',
        db_index=True
    )
    
    wechat_unionid = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        null=True,
        verbose_name='微信UnionID',
        help_text='用于多小程序/公众号统一账号'
    )
    
    # ========== 角色字段 ==========
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='角色'
    )
    
    # ========== 用户资料字段 ==========
    nickname = models.CharField(
        max_length=64,
        blank=True,
        default='',
        verbose_name='昵称'
    )
    
    real_name = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='真实姓名'
    )
    
    avatar = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='头像'
    )
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='性别'
    )
    
    birthday = models.DateField(
        blank=True,
        null=True,
        verbose_name='生日'
    )
    
    bio = models.TextField(
        blank=True,
        default='',
        max_length=500,
        verbose_name='个人简介'
    )
    
    # ========== 联系信息 ==========
    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^1[3-9]\d{9}$',
            message='请输入有效的中国大陆手机号'
        )],
        verbose_name='手机号'
    )
    
    address = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='地址'
    )
    
    # ========== 教育与职业 ==========
    education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        blank=True,
        null=True,
        verbose_name='学历'
    )
    
    occupation = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='职业'
    )
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['-date_joined']),
            models.Index(fields=['wechat_openid']),
        ]
    
    def __str__(self):
        if self.is_wechat_user:
            return f"微信用户({self.wechat_openid[:8]}...)"
        if self.nickname:
            return self.nickname
        if self.real_name:
            return self.real_name
        return self.username
    
    # ========== 属性方法 ==========
    @property
    def is_wechat_user(self):
        """判断是否为微信用户"""
        return bool(self.wechat_openid)
    
    @property
    def is_password_user(self):
        """判断是否为密码用户"""
        return self.has_usable_password()
    
    @property
    def login_type(self):
        """获取登录类型（动态计算，向后兼容）"""
        return 'wechat' if self.is_wechat_user else 'password'
    
    @property
    def display_name(self):
        """获取显示名称"""
        return self.nickname or self.real_name or self.username
    
    @property
    def age(self):
        """计算年龄"""
        if not self.birthday:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birthday.year - (
            (today.month, today.day) < (self.birthday.month, self.birthday.day)
        )
    
    @property
    def is_profile_complete(self):
        """判断资料是否完善"""
        return all([self.nickname, self.gender, self.birthday])