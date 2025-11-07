"""
Django 设置文件 - 认知照顾情绪监测系统
"""

# =============================================================================
# 基础导入和路径配置
# =============================================================================
from pathlib import Path
from datetime import timedelta
import dj_database_url
import os

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# 环境变量加载
# =============================================================================
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# 核心 Django 设置
# =============================================================================

# 安全密钥
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-b2#f(%-90xf8y7$54+l50r_p!eyfxd0xw2qu+uok+(z&_jc*px'
)

# 调试模式
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# 允许的主机
ALLOWED_HOSTS = (
    os.environ.get('ALLOWED_HOSTS', 'cg.aoxintech.com').split(',')
    if not DEBUG
    else ['*']
)

# 用户模型
AUTH_USER_MODEL = 'users.User'

# =============================================================================
# Django 核心应用配置
# =============================================================================

# 已安装的应用
INSTALLED_APPS = [
    # Django 内置应用
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # 第三方框架
    "corsheaders",
    "ninja",
    "ninja_extra",
    "ninja_jwt",
    'django_summernote',
    'import_export',
    
    # 自定义应用
    "apps.users",
    "apps.articles",
    "apps.journals",
    "apps.reports",
    "apps.scales",
    "apps.notifications",
    "apps.emotiontracker",
]

# 中间件
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URL 配置
ROOT_URLCONF = "config.urls"

# 模板配置
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

# WSGI 应用
WSGI_APPLICATION = "config.wsgi.application"

# =============================================================================
# 数据库配置
# =============================================================================

# 数据库 URL
DATABASE_URL = os.environ.get('DATABASE_URL')

# 数据库配置
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# 数据库连接池配置
DATABASES['default']['CONN_MAX_AGE'] = 600  # 连接保持时间（秒）
DATABASES['default']['CONN_HEALTH_CHECKS'] = True  # Django 4.1+ 连接健康检查

# 数据库性能优化配置（仅适配 PostgreSQL）
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000'  # 30秒查询超时
}

# =============================================================================
# 认证与授权
# =============================================================================

# 密码验证器
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# 认证后端
AUTHENTICATION_BACKENDS = [
    'apps.users.auth_backend.MultiAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# =============================================================================
# 国际化与本地化
# =============================================================================

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# =============================================================================
# 静态文件与媒体文件
# =============================================================================

# 静态文件
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# 媒体文件
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# 默认主键字段类型
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# 微信小程序配置
# =============================================================================

WECHAT_MINI_PROGRAM_APP_ID = os.environ.get('WECHAT_MINI_PROGRAM_APP_ID', '')
WECHAT_MINI_PROGRAM_APP_SECRET = os.environ.get('WECHAT_MINI_PROGRAM_APP_SECRET', '')

# =============================================================================
# JWT 认证配置
# =============================================================================

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
}

# =============================================================================
# CORS 与 CSRF 配置
# =============================================================================

# CORS 配置
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "https://cg.aoxintech.com",
    "http://cg.aoxintech.com",
]

# CSRF 配置
CSRF_TRUSTED_ORIGINS = [
    "https://cg.aoxintech.com",
    "http://cg.aoxintech.com",
]

# =============================================================================
# 缓存配置
# =============================================================================

CACHES = {
    # 默认内存缓存
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5分钟缓存超时
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # 最大缓存条目数
            'CULL_FREQUENCY': 3,  # 缓存清理频率
        }
    },
    
    # 数据库缓存
    'database': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
        'TIMEOUT': 600,  # 10分钟缓存超时
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
        }
    },
}

# =============================================================================
# 会话配置
# =============================================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24小时会话过期时间
SESSION_SAVE_EVERY_REQUEST = False  # 减少数据库写入
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# =============================================================================
# 缓存中间件配置
# =============================================================================

CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = ''
CACHE_MIDDLEWARE_ALIAS = 'default'

# =============================================================================
# 安全配置
# =============================================================================

# 基础安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 生产环境安全配置
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# =============================================================================
# 日志配置
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# =============================================================================
# 系统业务配置
# =============================================================================

# 用户相关配置
MIN_PASSWORD_LENGTH = 8
WECHAT_USER_NICKNAME_PREFIX = '微信用户'

# API 配置
API_VERSION = 'v1'
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# 文件上传配置
AVATAR_UPLOAD_PATH = 'avatars/'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']

# =============================================================================
# Django Summernote 配置
# =============================================================================

SUMMERNOTE_CONFIG = {
    'summernote': {
        'width': '100%',
        'height': '400',
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
        'placeholder': '请输入文章内容...',
    },
    'attachment_upload_to': 'summernote/',
    'attachment_filesize_limit': 5 * 1024 * 1024,  # 5MB
}