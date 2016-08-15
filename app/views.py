# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for, make_response
from flask_socketio import join_room
from app import app, socketio
from .game_master import GameMaster

USER_ID_COOKIE = app.config.get('USER_ID_COOKIE')

ANSWER_DURATION = app.config.get('ANSWER_DURATION')

game_master = GameMaster()


# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':

        # Check that player name is not empty
        if not request.form['player_name']:
            error = 'Please select a player name.'

        # Check that player name is not too long
        elif len(request.form['player_name']) > 50:
            error = 'Player name too long. Please try again.'

        # Register user and redirect him to the game
        else:
            # Create user
            user_id = game_master.create_player(request.form['player_name'])

            # Store user id in cookies
            resp = make_response(redirect(url_for('game')))
            resp.set_cookie(USER_ID_COOKIE, user_id)

            return resp

    return render_template('login.html', error=error)


@app.route('/')
@app.route('/game')
def game():
    # If user is not logged in, redirect him to the login page
    if request.cookies.get(USER_ID_COOKIE, None) not in game_master.players:
        return redirect(url_for('login'))

    return render_template('game.html',
                           ANSWER_DURATION=ANSWER_DURATION,
                           USER_ID_COOKIE=USER_ID_COOKIE)


@socketio.on('join')
def join_game(game_id):
    # Let user join the room hosting the game
    join_room(game_id)

    # If the game is not started yet, start it
    if game_id not in game_master.games:
        game_master.new_game(game_id)


@socketio.on('answer')
def store_answer(game_id, uuid, lat, lng):
    # Store new answer
    game_master.store_answer(game_id, uuid, lat, lng)
