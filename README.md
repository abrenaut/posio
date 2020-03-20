# Posio

A multiplayer geography game using Websockets.

Visit [https://posio.abrenaut.com/](https://posio.abrenaut.com/) for a live demo.

![Screenshot](screenshot.png)

## Developing

To download the project:

    git clone https://github.com/abrenaut/posio.git
    cd posio

To install dependencies:

    pip install -r requirements.txt

To override the configuration (optional):

    export POSIO_SETTINGS=/path/to/config.py

To run the application :

    python run.py

Open the following URL in your browser: [http://localhost:5000](http://localhost:5000)

### Using Docker

Run:

    docker-compose up

Wait until the environment builds and server is listening,
then go to <http://localhost:5000>.

## License

This project is under [MIT license](LICENSE).
