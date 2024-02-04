# Posio

A multiplayer geography game using Websockets.

Visit [https://posio.abrenaut.com/](https://posio.abrenaut.com/) for a live demo.

![Screenshot](screenshot.png)

## Quick start

1. Create a new [virtual environment](https://docs.python.org/3/library/venv.html) and activate it

```
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Run the application

```
flask --app posio run
```

4. Open the following URL in your browser: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Using Docker

1. Build the docker image

```
docker build . -t posio
```

2. Start the docker container

```
docker run -p 127.0.0.1:5000:5000 posio -m flask --app posio run --host=0.0.0.0
```

3. Open the following URL in your browser: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## License

This project is under [MIT license](LICENSE).
