FROM python:3.12.3-slim-bookworm AS app

WORKDIR /app

ARG UID=1000
ARG GID=1000

RUN apt-get update \
  && apt-get install -y --no-install-recommends libsqlite3-mod-spatialite binutils libproj-dev gdal-bin \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && groupadd -g "${GID}" python \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python \
  && mkdir -p /public_collected public \
  && chown python:python -R /public_collected /app

USER python


COPY --chown=python:python requirements.txt ./

RUN pip install --no-warn-script-location --no-cache-dir --user \
-r requirements.txt

ENV PYTHONUNBUFFERED="true" \
PYTHONPATH="." \
PATH="${PATH}:/home/python/.local/bin" \
USER="python"

COPY --chown=python:python . .
RUN mkdir -p /app/db

EXPOSE 8000

ENTRYPOINT ["python"]