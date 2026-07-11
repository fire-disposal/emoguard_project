from django.test import TestCase
from django.core.cache import cache
from apps.users.wechat_auth import WeChatAuthService


class WeChatReplayTests(TestCase):
    def setUp(self):
        cache.clear()
        self.svc = WeChatAuthService()

    def test_same_code_rejected_on_second_use(self):
        code = "a" * 32
        self.svc.validate_wechat_code(code)
        with self.assertRaises(Exception):
            self.svc.validate_wechat_code(code)
