from django.contrib.sessions.models import Session
from django.test import TestCase
from django.utils import timezone

from game import models, services


class FormatLeaderboardForUserTest(TestCase):
    maxDiff = None

    def test_score_for_city_question(self):
        leaderboard = []
        for i in range(100):
            session = Session.objects.create(
                expire_date=timezone.now(), session_key=f"session_{i}"
            )
            player = models.Player.objects.create(
                session=session,
                username=f"Player {i}",
            )
            leaderboard.append(
                models.LeaderboardRow(
                    player_id=player.id,
                    username=f"Player {i}",
                    rank=i,
                    score=100 - i,
                )
            )

        player50 = models.Player.objects.get(username="Player 50")
        shortened_leaderboard, player_rank, player_score = services.format_leaderboard(
            leaderboard, player50
        )

        self.assertEqual(
            shortened_leaderboard,
            [
                {"username": "Player 0", "rank": 0, "score": 100, "is_player": False},
                {"username": "Player 1", "rank": 1, "score": 99, "is_player": False},
                {"username": "Player 2", "rank": 2, "score": 98, "is_player": False},
                {"username": "Player 3", "rank": 3, "score": 97, "is_player": False},
                {"username": "Player 4", "rank": 4, "score": 96, "is_player": False},
                {"username": "Player 5", "rank": 5, "score": 95, "is_player": False},
                {"username": "Player 6", "rank": 6, "score": 94, "is_player": False},
                {"username": "Player 7", "rank": 7, "score": 93, "is_player": False},
                {"username": "Player 8", "rank": 8, "score": 92, "is_player": False},
                {"username": "Player 9", "rank": 9, "score": 91, "is_player": False},
                {"username": "You", "rank": 50, "score": 50, "is_player": True},
            ],
        )
        self.assertEqual(player_rank, 50)
        self.assertEqual(player_score, 50)

        player5 = models.Player.objects.get(username="Player 5")
        shortened_leaderboard, player_rank, player_score = services.format_leaderboard(
            leaderboard, player5
        )

        self.assertEqual(
            shortened_leaderboard,
            [
                {"username": "Player 0", "rank": 0, "score": 100, "is_player": False},
                {"username": "Player 1", "rank": 1, "score": 99, "is_player": False},
                {"username": "Player 2", "rank": 2, "score": 98, "is_player": False},
                {"username": "Player 3", "rank": 3, "score": 97, "is_player": False},
                {"username": "Player 4", "rank": 4, "score": 96, "is_player": False},
                {"username": "You", "rank": 5, "score": 95, "is_player": True},
                {"username": "Player 6", "rank": 6, "score": 94, "is_player": False},
                {"username": "Player 7", "rank": 7, "score": 93, "is_player": False},
                {"username": "Player 8", "rank": 8, "score": 92, "is_player": False},
                {"username": "Player 9", "rank": 9, "score": 91, "is_player": False},
            ],
        )
        self.assertEqual(player_rank, 5)
        self.assertEqual(player_score, 95)
