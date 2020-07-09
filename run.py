from app import socketio, app


PORT = app.config.get('PORT', 5000)

app.logger.info('Starting port {port}'.format(port=PORT))

socketio.run(app, host="0.0.0.0", port=PORT)
