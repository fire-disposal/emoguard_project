from unittest.mock import patch

from django.test import TestCase


class HealthEndpointTests(TestCase):
    def test_health_ok_returns_200_and_is_exempt_from_ssl_redirect(self):
        resp = self.client.get("/health/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "healthy")
        self.assertEqual(body["checks"]["database"], "healthy")

    def test_health_unhealthy_returns_503(self):
        with patch("config.health.cache.set", side_effect=Exception("redis down")):
            resp = self.client.get("/health/")
        self.assertEqual(resp.status_code, 503)
        self.assertEqual(resp.json()["status"], "unhealthy")
