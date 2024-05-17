import asyncio
from concurrent.futures import ThreadPoolExecutor

from django.core.management.base import BaseCommand

from game import models, services


class Command(BaseCommand):
    def handle(self, *args, **options):

        games = models.Game.objects.prefetch_related("question_set")

        executor = ThreadPoolExecutor(games.count())
        loop = asyncio.new_event_loop()

        for game in games:
            loop.run_in_executor(executor, services.game_loop, game)

        loop.run_forever()
