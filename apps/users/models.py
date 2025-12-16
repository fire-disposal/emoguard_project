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
    
    # ========== 用户基本资料字段 ==========
    real_name = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='真实姓名'
    )
    
    gender = models.CharField(
        max_length=10,
        blank=True,
        default='',
        verbose_name='性别'
    )
    
    age = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='年龄'
    )
    
    education = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='学历'
    )
    
    province = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='所在省份'
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='所在城市'
    )
    district = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='所在区县'
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
    
    # 用户信息完善状态
    is_profile_complete = models.BooleanField(
        default=False,
        verbose_name='信息已完善'
    )
    
    # 认知评估完成状态
    has_completed_cognitive_assessment = models.BooleanField(
        default=False,
        verbose_name='已完成初次认知评估'
    )

    # ========== 测评分数字段 ==========
    score_scd = models.FloatField(null=True, blank=True, verbose_name="SCD量表分数")
    score_mmse = models.FloatField(null=True, blank=True, verbose_name="MMSE量表分数")
    score_moca = models.FloatField(null=True, blank=True, verbose_name="MoCA量表分数")
    score_gad7 = models.FloatField(null=True, blank=True, verbose_name="GAD-7量表分数")
    score_phq9 = models.FloatField(null=True, blank=True, verbose_name="PHQ-9量表分数")
    score_adl = models.FloatField(null=True, blank=True, verbose_name="ADL量表分数")

    # ========== 情绪测试相关 ==========
    last_mood_tested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="上次每日情绪测试时间"
    )

    # ========== 分组字段 ==========
    group = models.CharField(
        max_length=64,
        blank=True,
        default='',
        verbose_name='分组'
    )

    # ========== 跟踪状态字段 ==========
    is_tracked = models.BooleanField(
        default=False,
        verbose_name='是否跟踪'
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['-date_joined']),
            models.Index(fields=['wechat_openid']),
        ]
    
    def __str__(self):
        if self.is_wechat_user:
            return f"微信用户({self.wechat_openid[:8]}...)"  # pyright: ignore[reportIndexIssue]
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
    def display_name(self):
        """获取显示名称"""
        return self.real_name or self.username
    
    def update_profile_complete_status(self):
        """更新信息完善状态"""
        required_fields = [
            self.real_name, self.gender, self.age, self.education,
            self.province, self.city, self.district, self.phone
        ]
        self.is_profile_complete = all(field for field in required_fields)
        return self.is_profile_complete