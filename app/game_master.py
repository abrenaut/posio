# -*- coding: utf-8 -*-

from app import socketio, app
from posio.game import GameTurn
from posio.city import get_random_city


class GameMaster:
    def __init__(self):
        self.current_turn = None

    def start(self):
        app.logger.info('Game master started')
        socketio.start_background_task(target=self.task)

    def task(self):

        while True:
            app.logger.info('Starting new turn')

            # Start the new turn
            self.current_turn = GameTurn()

            # Pick a random city for this turn
            city = get_random_city()

            socketio.emit('new_turn', {'city': city.name, 'country': city.country, 'country_code': city.country})

            # Give the user some time to answer
            socketio.sleep(app.config.get('ANSWER_DURATION'))

            app.logger.info('Ending turn')

            # Once the turn is over, send answers
            socketio.emit('end_of_turn',
                          {'answers': self.current_turn.answers,
                           'correct': {'name': city.name, 'lat': city.lat, 'lng': city.lng}})

            # Give the user some time between two turns
            socketio.sleep(app.config.get('RESULT_DURATION'))

    def store_answer(self, uuid, lat, lng):
        if self.current_turn:
            self.current_turn.store_answer(uuid, lat, lng)
