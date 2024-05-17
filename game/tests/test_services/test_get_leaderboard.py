from django.contrib.sessions.models import Session
from django.test import TestCase
from django.utils import timezone

from game import models, services


class EndCurrentTurnTests(TestCase):
    def setUp(self):
        self.game = models.Game.objects.create(name="Test Game")
        self.question_1 = models.Question.objects.create(
            game=self.game, label="Question 1", answer="POINT(0 0)"
        )
        self.question_2 = models.Question.objects.create(
            game=self.game, label="Question 2", answer="POINT(0 0)"
        )
        self.question_3 = models.Question.objects.create(
            game=self.game, label="Question 3", answer="POINT(0 0)"
        )
        self.game.current_instance = models.GameInstance.objects.create(game=self.game)
        self.game.save()
        session_1 = Session.objects.create(
            expire_date=timezone.now(), session_key="session_1"
        )
        session_2 = Session.objects.create(
            expire_date=timezone.now(), session_key="session_2"
        )
        session_3 = Session.objects.create(
            expire_date=timezone.now(), session_key="session_3"
        )
        self.player_1 = models.Player.objects.create(
            session=session_1, username="Player 1"
        )
        self.player_2 = models.Player.objects.create(
            session=session_2, username="Player 2"
        )
        self.player_3 = models.Player.objects.create(
            session=session_3, username="Player 3"
        )

    def test_end_current_turn(self):
        self.game_instance_2 = models.GameInstance.objects.create(game=self.game)
        self.game.current_instance = self.game_instance_2
        self.game.save()
        game_instance_question_1 = models.GameInstanceQuestion.objects.create(
            game_instance=self.game_instance_2, question=self.question_1
        )
        game_instance_question_2 = models.GameInstanceQuestion.objects.create(
            game_instance=self.game_instance_2, question=self.question_2
        )
        self.game_instance_2.current_question = game_instance_question_2

        models.PlayerAnswer.objects.create(
            game_instance_question=game_instance_question_1,
            player=self.player_1,
            answer="POINT(0 0)",
            score=100,
            distance_km=0,
        )

        models.PlayerAnswer.objects.create(
            game_instance_question=game_instance_question_1,
            player=self.player_2,
            answer="POINT(0 0)",
            score=100,
            distance_km=0,
        )

        models.PlayerAnswer.objects.create(
            game_instance_question=game_instance_question_2,
            player=self.player_1,
            answer="POINT(0 0)",
            score=100,
            distance_km=0,
        )

        leaderboard = services.get_leaderboard(self.game)

        self.assertEqual(
            leaderboard,
            [
                models.LeaderboardRow(
                    player_id=self.player_1.pk,
                    username="Player 1",
                    rank=1,
                    score=200,
                ),
                models.LeaderboardRow(
                    player_id=self.player_2.pk,
                    username="Player 2",
                    rank=2,
                    score=100,
                ),
            ],
        )
