import json
import logging
from collections import OrderedDict

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import get_template

from game import models, services

logger = logging.getLogger(__name__)


class GamePlayerConsumer(AsyncWebsocketConsumer):
    """
    Websocket consumer created when a player joins a game.

    This consumer is responsible for:
    - Sending new questions to the user.
    - Sending answers together with the leaderboard to the user.
    - Receiving the user's answer to the question.
    """

    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        session_key = self.scope["session"].session_key

        self.player = await database_sync_to_async(services.get_player)(
            session_key=session_key
        )

        self.game_group_name = f"game-{self.game_id}"

        await self.channel_layer.group_add(self.game_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        The only message we expect from the client is the user's answer to the question.
        """

        if not self.player:
            return

        try:
            text_data_json = json.loads(text_data)
            latitude = text_data_json["latitude"]
            longitude = text_data_json["longitude"]

            await database_sync_to_async(services.create_answer)(
                game_id=self.game_id,
                player=self.player,
                latitude=latitude,
                longitude=longitude,
            )
        except Exception:
            logger.exception("Invalid message received from WebSocket: %s", text_data)

    async def game_new_question(self, event):
        question_label = event["question_label"]
        question_image_url = event["question_image_url"]

        html = get_template("game/question.html").render(
            context={
                "question_label": question_label,
                "question_image_url": question_image_url,
            }
        )

        await self.send(text_data=html)

    async def game_answer(self, event):

        answer_json: str = event["answer_json"]
        answer_label: str = event["answer_label"]
        question_image_url: str = event["question_image_url"]
        leaderboard: list[models.LeaderboardRow] = event["leaderboard"]
        last_question_answers: OrderedDict = event["last_question_answers"]

        formatted_leaderboard, player_rank, player_score = services.format_leaderboard(
            leaderboard, self.player
        )

        context = {
            "answer_json": answer_json,
            "answer_label": answer_label,
            "question_image_url": question_image_url,
            "last_question_answers": last_question_answers,
            "last_question_answers_count": len(last_question_answers),
            "leaderboard": formatted_leaderboard,
            "leaderboard_answer_count": services.LEADERBOARD_ANSWER_COUNT,
            "player_rank": player_rank,
            "player_score": player_score,
            "player_count": len(leaderboard),
        }

        for i, last_question_answers in enumerate(last_question_answers):
            if i == 0:
                context["top_answer_json"] = last_question_answers["answer_json"]
            if self.player and last_question_answers["player_id"] == self.player.pk:
                context["player_answer_json"] = last_question_answers["answer_json"]
                context["last_question_player_score"] = last_question_answers["score"]
                context["last_question_player_rank"] = i + 1
                context["last_question_player_distance_km"] = int(
                    last_question_answers["distance_km"]
                )
                # We only need the user's answer and the top answer
                break

        html = get_template("game/answer.html").render(context=context)

        await self.send(text_data=html)
