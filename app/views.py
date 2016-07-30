# -*- coding: utf-8 -*-

from flask import render_template
from app import app, socketio
from .game_master import game_master_task, store_answer

game_master = None


@app.route('/')
@app.route('/map')
def render_map():
    return render_template('map.html',
                           MAPBOX_ID=app.config.get('MAPBOX_ID'),
                           MAPBOX_TOKEN=app.config.get('MAPBOX_TOKEN'))


@socketio.on('connect')
def handle_connect():
    app.logger.info('New client')

    # Start the game master a user is connected
    global game_master
    if not game_master:
        game_master = socketio.start_background_task(target=game_master_task)


@socketio.on('answer')
def handle_answer(uuid, lat, lng):
    # Store new answer
    store_answer(uuid, lat, lng)
