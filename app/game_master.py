# -*- coding: utf-8 -*-

from app import socketio, app
from posio.game import PosioGame
from uuid import uuid4
from collections import OrderedDict


class GameMaster:
    def __init__(self):
        self.started = False
        self.players = OrderedDict()
        self.games = {}

    def new_game(self, game_id):
        app.logger.info('Starting a new game with the id {game_id}'.format(game_id=game_id))

        # Create the game
        game = PosioGame(game_id, app.config.get('SCORE_MAX_DISTANCE'))

        # Register it
        self.games[game_id] = game

        # Start the task magine the game
        socketio.start_background_task(target=self.start, game=game)

    def start(self, game):
        while True:
            app.logger.info('Starting new turn')

            # Start a new turn
            game.new_turn()

            # Get the city for this turn
            city = game.current_city()

            socketio.emit('new_turn',
                          {'city': city['name'], 'country': city['country'], 'country_code': city['country']},
                          room=game.game_id)

            # Give the user some time to answer
            socketio.sleep(app.config.get('ANSWER_DURATION'))

            app.logger.info('Ending turn')

            ranked_answers = game.ranked_answers()

            # Once the turn is over, send answers
            socketio.emit('end_of_turn',
                          {'answers': ranked_answers,
                           'correct': {'name': city['name'], 'lat': city['latitude'], 'lng': city['longitude']}},
                          room=game.game_id)

            # Send updates to the leaderboard
            socketio.start_background_task(target=self.update_leaderboard, game=game)

            # Give the user some time between two turns
            socketio.sleep(app.config.get('RESULT_DURATION'))

    def store_answer(self, game_id, uuid, lat, lng):
        self.games[game_id].store_answer(uuid, lat, lng)

    def create_player(self, player_name):
        player_id = uuid4().hex

        self.players[player_id] = player_name

        return player_id

    def update_leaderboard(self, game):
        app.logger.info('Updating leaderboard')

        scores = game.get_ranked_scores()

        # Add player names for the 10 best score
        for score in scores[:10]:
            score['name'] = self.players[score['uuid']]

        socketio.emit('leaderboard_update', {'scores': scores}, room=game.game_id)
