# -*- coding: utf-8 -*-

from app import socketio, app
from posio.game import Game


class GameMaster:
    def __init__(self):
        # Init the list of games managed by this game master
        self.games = []

    def create_game(self, game_id, score_max_distance, max_response_time, leaderboard_answer_count,
                    between_turns_duration):
        app.logger.debug('Starting a new game with the id {game_id}'.format(game_id=game_id))

        # Create the game
        game = Game(game_id, score_max_distance, max_response_time, leaderboard_answer_count, between_turns_duration)

        # Register it
        self.games.append(game)

        # Start the game
        socketio.start_background_task(target=self.run_game, game=game)

        return game

    def get_game(self, game_id):
        # Return the game matching the given game_id
        for running_game in self.games:
            if running_game.game_id == game_id:
                return running_game
        else:
            return None

    @classmethod
    def run_game(cls, game):
        while True:
            # Start a new turn
            cls.start_turn(game)

            # Give the players some time to answer
            socketio.sleep(game.max_response_time)

            # End the turn
            cls.end_turn(game)

            # Send the new leaderboard to players
            cls.update_leaderboard(game)

            # Give the user some time between two turns
            socketio.sleep(game.between_turns_duration)

    @classmethod
    def start_turn(cls, game):
        app.logger.debug('Starting new turn for the game {game_id}'.format(game_id=game.game_id))

        # Start a new turn
        game.start_new_turn()

        # Get the city for this turn
        city = game.get_current_city()

        # Send the infos on the new city to locate to every players in the game
        socketio.emit('new_turn',
                      {'city': city['name'], 'country': city['country'], 'country_code': city['country']},
                      room=game.game_id)

    @classmethod
    def end_turn(cls, game):
        app.logger.debug('Ending turn for the game {game_id}'.format(game_id=game.game_id))

        # End current turn
        game.end_current_turn()

        # Rank answers
        ranked_players = game.get_current_turn_ranks()
        player_count = len(ranked_players)

        # Send the end of turn signal and the correct and best answer to every players in the game
        city = game.get_current_city()
        turn_results = {'correct_answer': {'name': city['name'],
                                           'lat': city['latitude'],
                                           'lng': city['longitude']}}

        if player_count > 0:
            turn_results['best_answer'] = {
                'distance': ranked_players[0].get_result(game.turn_number).distance,
                'lat': ranked_players[0].get_answer(game.turn_number).latitude,
                'lng': ranked_players[0].get_answer(game.turn_number).longitude
            }

        socketio.emit('end_of_turn', turn_results, room=game.game_id)

        # Then send individual player results
        for rank, player in enumerate(ranked_players):
            socketio.emit('player_results',
                          {
                              'rank': rank + 1,
                              'total': player_count,
                              'distance': player.get_result(game.turn_number).distance,
                              'score': player.get_result(game.turn_number).score,
                              'lat': player.get_answer(game.turn_number).latitude,
                              'lng': player.get_answer(game.turn_number).longitude
                          },
                          room=player.sid)

    @classmethod
    def update_leaderboard(cls, game):
        app.logger.debug('Updating leaderboard for the game {game_id}'.format(game_id=game.game_id))

        # Get a sorted list of all the scores
        scores = game.get_ranked_scores()  # Extract the top ten scores
        top_ten = [{'player_name': score['player'].name, 'score': score['score']} for score in scores[:10]]

        # Number of players
        total_player = len(scores)

        # Send top ten + player score and rank to each player
        for rank, score in enumerate(scores):
            socketio.emit('leaderboard_update', {
                'top_ten': top_ten,
                'total_player': total_player,
                'player_rank': rank,
                'player_score': score['score']
            }, room=score['player'].sid)
