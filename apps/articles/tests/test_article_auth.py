from django.test import TestCase, Client
from apps.articles.models import Article


class ArticleAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        Article.objects.create(title="draft-a", content="x", status="draft")

    def test_anonymous_cannot_list(self):
        resp = self.client.get("/api/articles/", secure=True)
        self.assertIn(resp.status_code, (401, 403))

    def test_anonymous_cannot_create(self):
        resp = self.client.post(
            "/api/articles/", data={"title": "h", "content": "c"},
            content_type="application/json", secure=True,
        )
        self.assertIn(resp.status_code, (401, 403))
