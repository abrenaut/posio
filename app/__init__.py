# -*- coding: utf-8 -*-

import logging
from os import environ
from flask import Flask
from flask_socketio import SocketIO
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_object('config')

# Override config if needed
if 'POSIO_SETTINGS' in environ:
    app.config.from_envvar('POSIO_SETTINGS')

cors_allowed_origins = app.config.get('CORS_ALLOWED_ORIGINS')
socketio = SocketIO(app, cors_allowed_origins=cors_allowed_origins)

from app import views  # noqa

file_handler = RotatingFileHandler('posio.log', 'a', 1 * 1024 * 1024, 10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.info('Startup')
