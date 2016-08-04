# -*- coding: utf-8 -*-

from app import socketio, app
from posio.game import PosioGame


class GameMaster:
    def __init__(self):
        self.game = PosioGame()

    def start(self):
        app.logger.info('Game master started')
        socketio.start_background_task(target=self.task)

    def task(self):
        while True:
            app.logger.info('Starting new turn')

            # Start a new turn
            self.game.new_turn()

            # Get the city for this turn
            city = self.game.get_current_city()

            socketio.emit('new_turn', {'city': city.name, 'country': city.country, 'country_code': city.country})

            # Give the user some time to answer
            socketio.sleep(app.config.get('ANSWER_DURATION'))

            app.logger.info('Ending turn')

            # Once the turn is over, send answers
            socketio.emit('end_of_turn',
                          {'answers': self.game.answers,
                           'correct': {'name': city.name, 'lat': city.lat, 'lng': city.lng}})

            # Give the user some time between two turns
            socketio.sleep(app.config.get('RESULT_DURATION'))

    def store_answer(self, uuid, lat, lng):
        self.game.store_answer(uuid, lat, lng)
