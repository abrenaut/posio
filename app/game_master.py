# -*- coding: utf-8 -*-

from app import socketio, app
from posio.game import PosioGame


class GameMaster:
    def __init__(self):
        self.game = PosioGame()

    def start(self):
        app.logger.info('Game master started')
        socketio.start_background_task(target=self.game_turn)

    def game_turn(self):
        while True:
            app.logger.info('Starting new turn')

            # Start a new turn
            self.game.new_turn()

            # Get the city for this turn
            city = self.game.current_city()

            socketio.emit('new_turn',
                          {'city': city['name'], 'country': city['country'], 'country_code': city['country']})

            # Give the user some time to answer
            socketio.sleep(app.config.get('ANSWER_DURATION'))

            app.logger.info('Ending turn')

            ranked_answers = self.game.ranked_answers()

            # Once the turn is over, send answers
            socketio.emit('end_of_turn',
                          {'answers': ranked_answers,
                           'correct': {'name': city['name'], 'lat': city['latitude'], 'lng': city['longitude']}})

            # Give the user some time between two turns
            socketio.sleep(app.config.get('RESULT_DURATION'))

    def store_answer(self, uuid, lat, lng):
        self.game.store_answer(uuid, lat, lng)
