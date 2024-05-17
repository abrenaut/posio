from collections import namedtuple
from datetime import timedelta

from django.contrib.gis.db import models
from django.contrib.sessions.models import Session


class Game(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    instructions = models.TextField(default="")
    time_to_answer_question = models.DurationField(default=timedelta(seconds=5))
    time_between_questions = models.DurationField(default=timedelta(seconds=3))
    current_instance = models.ForeignKey(
        "GameInstance",
        on_delete=models.SET_NULL,
        related_name="current_instance",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Question(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    label = models.CharField(max_length=250)
    image = models.FileField(upload_to="question/image/", null=True, blank=True)
    answer = models.GeometryField()
    answer_label = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.label


class GameInstance(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    current_question = models.ForeignKey(
        "GameInstanceQuestion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.game} instance"


class GameInstanceQuestion(models.Model):
    game_instance = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    asked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("game_instance", "question")
        indexes = [models.Index(fields=["asked_at"])]


class Player(models.Model):
    # PSA: Clearing sessions will delete the related players and their data
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)

    def __str__(self):
        return self.username


class PlayerAnswer(models.Model):
    game_instance_question = models.ForeignKey(
        GameInstanceQuestion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    answer = models.GeometryField()
    score = models.IntegerField()
    distance_km = models.FloatField()


LeaderboardRow = namedtuple(
    "LeaderboardRow",
    [
        "player_id",
        "username",
        "rank",
        "score",
    ],
)
