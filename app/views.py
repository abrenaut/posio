# -*- coding: utf-8 -*-

from flask import render_template
from app import app, socketio
from .game_master import GameMaster

game_master = None


@app.route('/')
@app.route('/map')
def render_map():
    return render_template('map.html', ANSWER_DURATION=app.config.get('ANSWER_DURATION'))


@socketio.on('connect')
def handle_connect():
    app.logger.info('New client')

    # Start the game master once a user is connected
    global game_master
    if not game_master:
        game_master = GameMaster()
        game_master.start()


@socketio.on('answer')
def handle_answer(uuid, lat, lng):
    # Store new answer
    game_master.store_answer(uuid, lat, lng)
