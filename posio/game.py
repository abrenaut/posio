# -*- coding: utf-8 -*-


class PosioGame:
    def __init__(self):
        self.answers = {}

    def start_turn(self):
        self.answers = {}

    def store_answer(self, uuid, lat, lng):
        self.answers[uuid] = {'lat' : lat, 'lng': lng}
