# -*- coding: utf-8 -*-

from app import socketio, app

pos = {}
updated_pos = []


def store_pos(lat, lng, timestamp, fp):
    # Store a user position and append it to the list of positions to update
    pos[fp] = {'lat': lat, 'long': lng, 'timestamp': timestamp, 'fp': fp}
    updated_pos.append(fp)


def position_update_task():
    app.logger.info('Position update task started')

    while True:
        # If new user positions available, send them to clients
        if updated_pos:
            app.logger.info('Sending new positions')
            socketio.emit('update_pos', {'pos': [pos[fp] for fp in updated_pos]})

            # Reset the list of user positions to update
            del updated_pos[:]

        socketio.sleep(1)
