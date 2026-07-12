"""测试专用配置:内存 SQLite、同步 Celery、显式 JWT 签名密钥。
用法: uv run python manage.py test --settings=config.settings_test
"""
import os

os.environ.setdefault("JWT_SIGNING_KEY", "test-only-signing-key-not-for-production")
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-not-for-production")

from config.settings import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

CELERY_TASK_ALWAYS_EAGER = True

# 显式提供签名密钥,规避 fail-fast 校验
JWT_SIGNING_KEY = "test-only-signing-key-not-for-production"
NINJA_JWT = {**NINJA_JWT, "SIGNING_KEY": JWT_SIGNING_KEY}  # noqa: F405

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
