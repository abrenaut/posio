# -*- coding: utf-8 -*-

from posio.city import get_cities


class PosioGame:
    def __init__(self):
        self.cities = get_cities()
        self.answers = {}
        self.turn_number = 0

    def get_current_city(self):
        # Return a different city for each turn
        return self.cities[self.turn_number % len(self.cities)]

    def new_turn(self):
        # Reset answers
        self.answers.clear()

        # Update turn number
        self.turn_number += 1

    def store_answer(self, uuid, lat, lng):
        self.answers[uuid] = {'lat': lat, 'lng': lng}
