FROM python:3-alpine
WORKDIR /posio
COPY requirements.txt /posio
RUN pip install -r requirements.txt
COPY . /posio
CMD ["flask", "--app", "posio", "run", "--host=0.0.0.0"]