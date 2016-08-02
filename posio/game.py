# -*- coding: utf-8 -*-


class GameTurn:
    def __init__(self):
        self.answers = {}

    def store_answer(self, uuid, lat, lng):
        self.answers[uuid] = {'lat': lat, 'lng': lng}
