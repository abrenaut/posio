# -*- coding: utf-8 -*-

from flask import render_template, request
from flask_socketio import join_room, leave_room
from app import app, socketio
from .game_master import GameMaster

game_master = GameMaster()


@app.route('/')
@app.route('/game')
def game():
    return render_template('game.html', ANSWER_DURATION=app.config.get('ANSWER_DURATION'))


@socketio.on('join_game')
def join_game(game_id, player_name):
    # Let player join the room hosting the game
    join_room(game_id)

    # If the game is not started yet, start it
    if game_id not in game_master.games:
        game_master.create_game(game_id)

    # Add the player to the game
    app.logger.info('{player_name} has joined the game {game_id}'.format(game_id=game_id, player_name=player_name))
    game_master.games[game_id].add_player(request.sid, player_name)


@socketio.on('disconnect')
def leave_game():
    for game_id in game_master.games:
        if request.sid in game_master.games[game_id].players:
            app.logger.info('{player_name} has left the game {game_id}'.format(game_id=game_id,
                                                                               player_name=game_master.games[
                                                                                   game_id].get_player(
                                                                                   request.sid)['name']))
            game_master.games[game_id].remove_player(request.sid)


@socketio.on('answer')
def store_answer(game_id, lat, lng):
    # Store new answer
    game_master.games[game_id].store_answer(request.sid, lat, lng)
