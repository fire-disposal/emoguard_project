from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja_jwt.tokens import RefreshToken
from config.jwt_auth_adapter import refresh_access_token

User = get_user_model()


class RefreshRotationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="openid_x", role="user")

    def test_refresh_returns_new_access_and_refresh(self):
        tokens = RefreshToken.for_user(self.user)
        result = refresh_access_token(str(tokens))
        self.assertIsNotNone(result)
        self.assertIn("access", result)
        self.assertIn("refresh", result)
        self.assertNotEqual(result["refresh"], str(tokens))

    def test_old_refresh_is_blacklisted_after_rotation(self):
        tokens = RefreshToken.for_user(self.user)
        old = str(tokens)
        refresh_access_token(old)
        second = refresh_access_token(old)
        self.assertIsNone(second)

    def test_invalid_token_returns_none(self):
        self.assertIsNone(refresh_access_token("not-a-token"))
