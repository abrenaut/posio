# -*- coding: utf-8 -*-

from app import socketio, app
from posio.game import PosioGame


class GameMaster:
    def __init__(self):
        self.games = {}

    def create_game(self, game_id):
        app.logger.info('Starting a new game with the id {game_id}'.format(game_id=game_id))

        # Create the game
        game = PosioGame(game_id, app.config.get('SCORE_MAX_DISTANCE'))

        # Register it
        self.games[game_id] = game

        # Start the game
        socketio.start_background_task(target=self.start_game, game=game)

    def start_game(self, game):
        while True:
            app.logger.info('Starting new turn')

            # Start a new turn
            game.start_new_turn()

            # Get the city for this turn
            city = game.get_current_city()

            # Send the infos on the new city to locate to every players in the game
            socketio.emit('new_turn',
                          {'city': city['name'], 'country': city['country'], 'country_code': city['country']},
                          room=game.game_id)

            # Give the players some time to answer
            socketio.sleep(app.config.get('ANSWER_DURATION'))

            app.logger.info('Ending turn')

            # Rank answers
            ranked_answers = game.get_ranked_answers()
            answer_count = len(ranked_answers)

            # Send the end of turn signal and the correct and best answer to every players in the game
            global_results = {'correct_answer': {'name': city['name'],
                                                 'lat': city['latitude'],
                                                 'lng': city['longitude']}}

            if answer_count:
                global_results['best_answer'] = {
                    'distance': ranked_answers[0]['distance'],
                    'lat': ranked_answers[0]['latitude'],
                    'lng': ranked_answers[0]['longitude']
                }

            socketio.emit('end_of_turn', global_results, room=game.game_id)

            # Then send player results
            for rank, player_answer in enumerate(ranked_answers):
                socketio.emit('player_results',
                              {
                                  'rank': rank + 1,
                                  'total': answer_count,
                                  'distance': player_answer['distance'],
                                  'score': player_answer['score'],
                                  'lat': player_answer['latitude'],
                                  'lng': player_answer['longitude']
                              },
                              room=player_answer['sid'])

            # Send updates to the leaderboard
            socketio.start_background_task(target=self.update_leaderboard, game=game)

            # Give the user some time between two turns
            socketio.sleep(app.config.get('RESULT_DURATION'))

    def update_leaderboard(self, game):
        app.logger.info('Updating leaderboard')

        # Get a sorted list of all the scores
        scores = game.get_ranked_scores()

        # Extract the top ten scores
        top_ten = [{'player_name': game.players[score['sid']]['name'], 'score': score['score']} for score in
                   scores[:10]]

        # Send top ten + player score and rank to each player
        for rank, player in enumerate(scores):
            socketio.emit('leaderboard_update', {
                'top_ten': top_ten,
                'player_rank': rank,
                'player_score': player['score']
            }, room=player['sid'])
