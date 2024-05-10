import datetime
import json

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from game import models


class Command(BaseCommand):

    def handle(self, *args, **options):

        game = models.Game.objects.create(
            name="Cities",
            slug="cities",
            title="Locate Cities",
            description="Locate a city on the map.",
            instructions="You'll be given a list of cities that you must locate by clicking on the map",
            time_to_answer_question=datetime.timedelta(seconds=5),
            time_between_questions=datetime.timedelta(seconds=3),
        )

        with open("game/data/cities.json") as f:
            cities = json.load(f)

            for city in cities:

                city_name = city["name"]
                country_name = city["country"]
                city_location = Point(city["longitude"], city["latitude"])

                models.Question.objects.create(
                    game=game,
                    label=f"Locate {city_name} ({country_name})",
                    answer=city_location,
                )
