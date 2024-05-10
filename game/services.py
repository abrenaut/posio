import logging
import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.gis import geos
from django.db.models import OuterRef, Sum
from django.http import HttpRequest

from game import models

logger = logging.getLogger(__name__)


# Maximum score a user can get for a question.
MAX_SCORE = 2000

# Number of questions to consider when calculating the leaderboard.
LEADERBOARD_ANSWER_COUNT = 20

# Maximum number of rows to show in the leaderboard.
MAX_ROWS_IN_LEADERBOARD = 10


def create_player(request: HttpRequest, username: str) -> models.Player:
    """Create a new player with the given username and session key."""

    if not request.session.exists(request.session.session_key):
        request.session.create()

    player, _ = models.Player.objects.update_or_create(
        session_id=request.session.session_key,
        defaults={"username": username},
    )

    return player


def calculate_score(question: models.Question, answer: geos.Point) -> tuple[int, int]:
    """
    Calculate how close the user's answer is to the correct answer and return
    the distance and the score.
    The score is based on the distance between the user's answer and the correct
    answer.
    """

    distance_km = question.answer.distance(answer) * 100

    score = MAX_SCORE - distance_km

    return distance_km, max(0, round(score))


def get_player(session_key: str) -> models.Player:
    """Get the player for the given session key."""

    player = None

    if session_key:
        try:
            player = models.Player.objects.get(session_id=session_key)
        except models.Player.DoesNotExist:
            return None

    return player


def create_answer(
    game_id: int,
    player: models.Player,
    latitude: float,
    longitude: float,
) -> models.PlayerAnswer:
    """Update a user answer for the current game instance question."""

    player_answer = None

    game = models.Game.objects.select_related(
        "current_instance",
        "current_instance__current_question",
    ).get(pk=game_id)
    game_instance_question = game.current_instance.current_question

    if game_instance_question:

        answer = geos.Point(longitude, latitude)
        distance_km, score = calculate_score(game_instance_question.question, answer)

        player_answer, _ = models.PlayerAnswer.objects.update_or_create(
            game_instance_question=game_instance_question,
            player=player,
            defaults={"answer": answer, "score": score, "distance_km": distance_km},
        )

    return player_answer


def create_game_instance(game: models.Game) -> models.GameInstance:
    """Create a new game instance for the given game."""

    game_instance = models.GameInstance.objects.create(game=game)
    game.current_instance = game_instance
    game.save(update_fields=["current_instance"])

    return game_instance


def start_new_turn(
    game_instance: models.GameInstance,
    question: models.Question,
) -> models.GameInstanceQuestion:
    """Start a new turn for the given game instance with a new question."""

    game_instance_question = models.GameInstanceQuestion.objects.create(
        game_instance=game_instance,
        question=question,
    )
    game_instance.current_question = game_instance_question
    game_instance.save(update_fields=["current_question"])

    return game_instance_question


def end_current_turn(game_instance: models.GameInstance):
    """End the current turn for the given game instance."""

    game_instance.current_question = None
    game_instance.save(update_fields=["current_question"])


def get_leaderboard(game: models.Game) -> list[models.LeaderboardRow]:
    """
    Return the current leaderboard with the total score for each player and
    the score for the question passed as an argument.
    """

    # Leaderboard is calculated based on the last N questions asked.
    leaderboard_questions = models.GameInstanceQuestion.objects.filter(
        game_instance__game=game,
    ).order_by("-asked_at")[:LEADERBOARD_ANSWER_COUNT]

    leaderboard = (
        models.Player.objects.annotate(
            total_score=models.PlayerAnswer.objects.filter(
                player_id=OuterRef("pk"),
                game_instance_question_id__in=leaderboard_questions.values_list(
                    "id",
                    flat=True,
                ),
            )
            .values("player")
            .annotate(total_score=Sum("score"))
            .values("total_score"),
        )
        .filter(total_score__gt=0)
        .order_by("-total_score")
        .values("pk", "username", "total_score")[:1000]
    )

    return [
        models.LeaderboardRow(
            player_id=row["pk"],
            username=row["username"],
            rank=i + 1,
            score=row["total_score"],
        )
        for i, row in enumerate(leaderboard)
    ]


def get_serialized_question_answers(
    game_instance_question: models.GameInstanceQuestion,
) -> list[dict]:
    """
    Get a question's answers and serialize them so they can't be sent to
    websocket consumers.
    """

    question_answers = (
        game_instance_question.playeranswer_set.filter(
            game_instance_question=game_instance_question
        )
        .order_by("-score")
        .values("player_id", "score", "distance_km", "answer")[:1000]
    )

    serialized_question_answers = [
        {
            "player_id": answer["player_id"],
            "score": answer["score"],
            "distance_km": answer["distance_km"],
            "answer_json": answer["answer"].json,
        }
        for answer in question_answers
    ]

    return serialized_question_answers


def format_leaderboard(
    leaderboard: list[models.LeaderboardRow],
    player: models.Player,
) -> tuple[list[models.LeaderboardRow], int | None, int]:
    """
    Shorten a leaderboard to only show the player's position and the top N
    players.
    Replace the player's username with "You" and highlight the player's row.

    Return the formatted leaderboard, the player's rank, and the player's score.
    """

    player_in_leaderboard = False
    formatted_leaderboard, player_rank, player_score = [], None, 0
    for row in leaderboard:
        player_id, username, rank, score = row
        if player and player_id == player.pk:
            formatted_leaderboard.append(
                {
                    "username": "You",
                    "rank": rank,
                    "score": score,
                    "is_player": True,
                }
            )
            player_in_leaderboard = True
            player_rank, player_score = rank, score
        elif len(formatted_leaderboard) < MAX_ROWS_IN_LEADERBOARD:
            formatted_leaderboard.append(
                {
                    "username": username,
                    "rank": rank,
                    "score": score,
                    "is_player": False,
                }
            )

        if (
            player_in_leaderboard
            and len(formatted_leaderboard) >= MAX_ROWS_IN_LEADERBOARD
        ):
            break

    return formatted_leaderboard, player_rank, player_score


def game_loop(game: models.Game):
    """
    Main game loop that sends questions to the players and sends the updated
    leaderboard after each question.
    """

    logger.info("Game thread started for %s", game.name)

    channel_layer = get_channel_layer()

    while True:

        game_instance = create_game_instance(game)

        # Shuffle the questions to be asked for the new game instance
        questions = game.question_set.order_by("?")

        for question in questions:
            logger.info("Sending question %s", question.label)

            game_instance_question = start_new_turn(game_instance, question)

            question_image_url = None
            if game_instance_question.question.image:
                question_image_url = game_instance_question.question.image.url

            async_to_sync(channel_layer.group_send)(
                f"game-{game.id}",
                {
                    "type": "game.new.question",
                    "question_label": game_instance_question.question.label,
                    "question_image_url": question_image_url,
                },
            )

            time.sleep(game.time_to_answer_question.total_seconds())

            end_current_turn(game_instance)

            leaderboard = get_leaderboard(game)
            serialized_last_question_answers = get_serialized_question_answers(
                game_instance_question
            )

            """
            Send the answer to the question together with all the information
            required to update the frontend.
            By fetching all this data at once, we avoid making multiple queries
            to the database for each player currently connected to the game.
            """
            async_to_sync(channel_layer.group_send)(
                f"game-{game.id}",
                {
                    "type": "game.answer",
                    "answer_json": question.answer.json,
                    "answer_label": question.answer_label,
                    "question_image_url": question_image_url,
                    "leaderboard": leaderboard,
                    "last_question_answers": serialized_last_question_answers,
                },
            )

            time.sleep(game.time_between_questions.total_seconds())
