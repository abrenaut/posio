from django.contrib.gis import geos
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.test import TestCase
from django.utils import timezone

from game import models, services


class CreateAnswerTests(TestCase):

    def setUp(self):
        self.game = models.Game.objects.create(name="Test Game")
        self.question = models.Question.objects.create(
            game=self.game,
            label="Locate Melbourne",
            answer=geos.Point(37.8136, 144.9631),
        )
        self.game.current_instance = models.GameInstance.objects.create(game=self.game)
        self.game.save()
        self.session = SessionStore()
        self.session.save()
        session = Session.objects.create(
            expire_date=timezone.now(), session_key="session_1"
        )
        self.player = models.Player.objects.create(session=session, username="Player 1")

    def test_create_answer(self):
        game_instance_question = models.GameInstanceQuestion.objects.create(
            game_instance=self.game.current_instance,
            question=self.question,
        )
        self.game.current_instance.current_question = game_instance_question
        self.game.current_instance.save()

        services.create_answer(
            game_id=self.game.id,
            player=self.player,
            latitude=0,
            longitude=0,
        )

        self.assertTrue(
            models.PlayerAnswer.objects.filter(
                game_instance_question=game_instance_question,
                player=self.player,
            ).exists(),
            "PlayerAnswer object was not created",
        )

        services.create_answer(
            game_id=self.game.id,
            player=self.player,
            latitude=1,
            longitude=1,
        )

        self.assertTrue(
            models.PlayerAnswer.objects.filter(
                game_instance_question=game_instance_question,
                player=self.player,
            )
            .first()
            .answer.x
            == 1,
            "PlayerAnswer object was not updated",
        )

    def test_create_answer_after_turn_finished(self):
        self.game.current_instance.current_question = None
        self.game.current_instance.save()

        player_answer = services.create_answer(
            game_id=self.game.id,
            player=self.player,
            latitude=1,
            longitude=1,
        )

        self.assertIsNone(
            player_answer, "PlayerAnswer should not be created after turn is finished"
        )
