from django.test import SimpleTestCase
from django.conf import settings


class JwtSigningKeyTests(SimpleTestCase):
    def test_signing_key_is_decoupled_from_secret_key(self):
        self.assertIn("SIGNING_KEY", settings.NINJA_JWT)
        self.assertEqual(
            settings.NINJA_JWT["SIGNING_KEY"], settings.JWT_SIGNING_KEY
        )

    def test_signing_key_not_the_insecure_secret_fallback(self):
        self.assertNotIn(
            "django-insecure", settings.NINJA_JWT["SIGNING_KEY"]
        )
