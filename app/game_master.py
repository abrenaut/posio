# -*- coding: utf-8 -*-

from app import socketio, app
from posio.game import PosioGame
from posio.city import get_random_city

game = PosioGame()


def game_master_task():
    app.logger.info('Game master started')

    while True:
        app.logger.info('Starting new turn')

        game.start_turn()

        city = get_random_city()

        socketio.emit('new_turn', {'city': city.name, 'country': city.country})

        socketio.sleep(5)

        app.logger.info('Ending turn')

        socketio.emit('end_of_turn', {'answers': game.answers, 'correct': {'lat': city.lat, 'lng': city.lng}})

        socketio.sleep(5)


def store_answer(uuid, lat, lng):
    game.store_answer(uuid, lat, lng)
