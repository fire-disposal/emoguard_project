from django.test import TestCase
from apps.feedback.serializers import FeedbackCreateSchema
from pydantic import ValidationError


class RatingValidationTest(TestCase):
    def test_rating_zero_rejected(self):
        with self.assertRaises(ValidationError):
            FeedbackCreateSchema(rating=0)

    def test_rating_six_rejected(self):
        with self.assertRaises(ValidationError):
            FeedbackCreateSchema(rating=6)

    def test_rating_valid(self):
        obj = FeedbackCreateSchema(rating=5, content="ok")
        self.assertEqual(obj.rating, 5)
