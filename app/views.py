# -*- coding: utf-8 -*-

from flask import render_template
from app import app, socketio
from .gis import store_pos, pos, position_update_task
from flask_socketio import emit

task = None


@app.route('/')
@app.route('/map')
def render_map():
    return render_template('map.html',
                           MAPBOX_ID=app.config.get('MAPBOX_ID'),
                           MAPBOX_TOKEN=app.config.get('MAPBOX_TOKEN'))


@socketio.on('connect')
def handle_connect():
    app.logger.info('New client')

    # Start the position update task once a user is connected
    global task
    if not task:
        task = socketio.start_background_task(target=position_update_task)

    # Send known positions to the user to initialize his map
    emit('init_pos', {'pos': [pos[fp] for fp in pos]})


@socketio.on('send_pos')
def handle_send_pos(lat, lng, timestamp, fp):
    # Store new user position
    store_pos(lat, lng, timestamp, fp)
