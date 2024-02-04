import logging
from os import environ

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object('posio.config')

# Override config if needed
if 'POSIO_SETTINGS' in environ:
    app.config.from_envvar('POSIO_SETTINGS')

cors_allowed_origins = app.config.get('CORS_ALLOWED_ORIGINS')
socketio = SocketIO(app, cors_allowed_origins=cors_allowed_origins)

from posio import views  # noqa

app.logger.setLevel(logging.INFO)
app.logger.info('Startup')
