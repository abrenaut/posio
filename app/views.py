# -*- coding: utf-8 -*-

from flask import render_template, request
from app import app, socketio
from .game_master import GameMaster

# The max distance used to compute players score
SCORE_MAX_DISTANCE = app.config.get('SCORE_MAX_DISTANCE')

# The time given to a player to answer a question
MAX_RESPONSE_TIME = app.config.get('MAX_RESPONSE_TIME')

# The time between two turns
TIME_BETWEEN_TURNS = app.config.get('TIME_BETWEEN_TURNS')

# How many answers are used to compute user score
LEADERBOARD_ANSWER_COUNT = app.config.get('LEADERBOARD_ANSWER_COUNT')

# Are players allowed to give multiple answers to the same question
ALLOW_MULTIPLE_ANSWER = app.config.get('ALLOW_MULTIPLE_ANSWER')

# How many zoom level are allowed
ZOOM_LEVEL = min(app.config.get('ZOOM_LEVEL'), 2)

# CDN Url for static ressources
CDN_URL = app.config.get('CDN_URL')

# Create the game master and start the game
game_master = GameMaster(SCORE_MAX_DISTANCE,
                         LEADERBOARD_ANSWER_COUNT,
                         MAX_RESPONSE_TIME,
                         TIME_BETWEEN_TURNS)
game_master.start_game()


@app.route('/')
@app.route('/game')
def render_game():
    return render_template('game.html',
                           MAX_RESPONSE_TIME=MAX_RESPONSE_TIME,
                           LEADERBOARD_ANSWER_COUNT=LEADERBOARD_ANSWER_COUNT,
                           ALLOW_MULTIPLE_ANSWER=ALLOW_MULTIPLE_ANSWER,
                           ZOOM_LEVEL=ZOOM_LEVEL,
                           CDN_URL=CDN_URL)


@socketio.on('join_game')
def join_game(player_name):
    app.logger.info('{player_name} has joined the game'.format(
        player_name=player_name))

    # Add the player to the game
    game_master.game.add_player(request.sid, player_name)


@socketio.on('disconnect')
def leave_games():
    app.logger.info('A player has left the game')
    game_master.game.remove_player(request.sid)


@socketio.on('answer')
def store_answer(latitude, longitude):
    game_master.game.store_answer(request.sid, latitude, longitude)
