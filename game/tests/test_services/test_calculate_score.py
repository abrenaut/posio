from django.contrib.gis import geos
from django.test import TestCase

from game import models, services


class CalculateScoreTests(TestCase):

    def setUp(self):
        self.game = models.Game.objects.create(name="Test Game")

    def test_score_for_city_question(self):
        melbourne_question = models.Question.objects.create(
            game=self.game,
            label="Locate Melbourne",
            answer=geos.Point(37.8136, 144.9631),
        )
        fougeres_point = geos.Point(48.3516, 1.2046)
        sydney_point = geos.Point(33.8688, 151.2093)

        _, score = services.calculate_score(melbourne_question, fougeres_point)
        self.assertEqual(score, 0, "The score should be 0")

        _, score = services.calculate_score(
            melbourne_question, melbourne_question.answer
        )
        self.assertEqual(
            score,
            services.MAX_SCORE,
            f"The score should be {services.MAX_SCORE}",
        )

        _, score = services.calculate_score(melbourne_question, sydney_point)
        self.assertTrue(
            0 < score < services.MAX_SCORE,
            f"The score should be between 0 and {services.MAX_SCORE}",
        )
