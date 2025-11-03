"""
改进的Django设置文件
支持多种认证方式
"""
from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-b2#f(%-90xf8y7$54+l50r_p!eyfxd0xw2qu+uok+(z&_jc*px"

# 使用改进的用户模型
AUTH_USER_MODEL = 'users.User'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # --- 第三方框架 ---
    "ninja",
    "ninja_extra",
    "ninja_jwt",
    'django_summernote',
    # --- 模块 ---
    "apps.users",
    "apps.articles",
    "apps.journals",
    "apps.reports",
    "apps.scales",
    "apps.notifications",
]
    
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ========== 微信小程序配置 ==========
# 从环境变量获取，确保生产环境安全
WECHAT_MINI_PROGRAM_APP_ID = os.environ.get('WECHAT_MINI_PROGRAM_APP_ID', '')
WECHAT_MINI_PROGRAM_APP_SECRET = os.environ.get('WECHAT_MINI_PROGRAM_APP_SECRET', '')

# 微信小程序安全配置
WECHAT_API_TIMEOUT = 10  # 微信API请求超时时间（秒）
WECHAT_CODE_EXPIRE_TIME = 300  # 微信code缓存过期时间（秒）
WECHAT_MAX_LOGIN_ATTEMPTS = 5  # 最大登录尝试次数
WECHAT_LOGIN_LOCKOUT_TIME = 300  # 登录锁定时间（秒）

# ========== Django Ninja JWT配置 ==========
NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('ninja_jwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'users.User',
    # 增强JWT安全性
    'TOKEN_OBTAIN_SERIALIZER': 'ninja_jwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'ninja_jwt.serializers.TokenRefreshSerializer',
}

# ========== 认证配置 ==========
# 使用改进的多认证后端
AUTHENTICATION_BACKENDS = [
    'apps.users.auth_backend.MultiAuthBackend',  # 统一认证后端
    'django.contrib.auth.backends.ModelBackend', # Django默认认证（备用）
]

# ========== 请求频率限制配置 ==========
# 微信登录频率限制
WECHAT_LOGIN_RATE_LIMIT = '5/m'  # 每分钟最多5次
WECHAT_LOGIN_RATE_LIMIT_KEY = 'ip'  # 基于IP限制

# 管理员登录频率限制
ADMIN_LOGIN_RATE_LIMIT = '3/m'  # 每分钟最多3次
ADMIN_LOGIN_RATE_LIMIT_KEY = 'ip'  # 基于IP限制

# ========== 安全配置 ==========
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 生产环境安全配置（当DEBUG=False时生效）
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1年
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ========== 权限配置 ==========
# 管理员权限组
ADMIN_GROUP_NAME = 'administrators'
USER_GROUP_NAME = 'users'

# ========== 日志配置 ==========
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'auth_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'auth.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.users': {
            'handlers': ['console', 'auth_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 创建日志目录
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ========== CORS配置 ==========
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ========== 缓存配置 ==========
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# ========== 安全配置 ==========
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ========== 用户相关配置 ==========
# 用户密码最小长度
MIN_PASSWORD_LENGTH = 8

# 微信用户默认昵称前缀
WECHAT_USER_NICKNAME_PREFIX = '微信用户'

# 管理员创建用户的默认设置
ADMIN_CREATE_USER_DEFAULTS = {
    'is_active': True,
    'login_type': 'password',
}

# ========== API配置 ==========
# API版本
API_VERSION = 'v1'

# 分页设置
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ========== 文件上传配置 ==========
# 头像上传路径
AVATAR_UPLOAD_PATH = 'avatars/'

# 文件大小限制 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# 允许的图片格式
ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']

# ========== Django Summernote 配置 ==========
SUMMERNOTE_CONFIG = {
    'summernote': {
        'width': '200%',
        'height': '600',  # 增加高度
        'lang': 'zh-CN',
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'italic', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],
        'codemirror': {  # 代码高亮配置
            'theme': 'monokai',
        },
        'placeholder': '请输入文章内容...',
    },
    'attachment_model': 'django_summernote.Attachment',
    'attachment_upload_to': 'summernote/',
    'attachment_filesize_limit': 5 * 1024 * 1024,  # 5MB
}