from django.test import TestCase, Client
from apps.reports.models import HealthReport


class ReportsAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        HealthReport.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            assessment_id=1, report_type="t", overall_risk="低风险",
            summary="s", recommendations=[], professional_advice="a",
            trend_analysis="ta", trend_data={},
        )

    def test_anonymous_cannot_get_report(self):
        resp = self.client.get("/api/reports/1", secure=True)
        self.assertIn(resp.status_code, (401, 403))
