import datetime
import json

from django.contrib.gis.geos import GEOSGeometry
from django.core.files import File
from django.core.management.base import BaseCommand

from game import models


class Command(BaseCommand):

    def handle(self, *args, **options):

        game = models.Game.objects.create(
            name="Country Flags",
            slug="flags",
            title="Country Flags",
            description="Guess and locate the country by its flag.",
            instructions="You'll be shown country flags that you must locate by clicking on the map",
            time_to_answer_question=datetime.timedelta(seconds=5),
            time_between_questions=datetime.timedelta(seconds=3),
        )

        with open("game/data/countries.json") as f:
            countries = json.load(f)

            for country in countries:

                if not country["unMember"]:
                    continue

                geometry_data = country["geometry"]
                country_name = country["name"]

                country_geometry_str = json.dumps(geometry_data)
                country_geometry = GEOSGeometry(country_geometry_str)

                question = models.Question(
                    game=game,
                    label="Locate the country corresponding to the flag",
                    answer=country_geometry,
                    answer_label=country_name,
                )

                country_flag_path = f"game/data/flags/{country["flag"]}"
                with open(country_flag_path, "rb") as country_flag_svg:
                    question.image.save(
                        country["flag"],
                        File(country_flag_svg),
                        save=True,
                    )
                question.save()
