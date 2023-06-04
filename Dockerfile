FROM node:16.20 AS frontend

ENV APP_HOME=/opt/starburger/web

WORKDIR $APP_HOME
COPY package*.json ./

RUN npm ci --include=dev

COPY bundles-src ./bundles-src

RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

FROM python:3.9.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/opt/starburger
ENV APP_HOME=/opt/starburger/web

RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/staticfiles
RUN mkdir -p $APP_HOME/media

WORKDIR $APP_HOME
COPY ./requirements.txt .

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev git \
    && pip install --upgrade pip setuptools \
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY --from=frontend $APP_HOME/bundles ./bundles
COPY .git ./.git
COPY address ./address
COPY assets ./assets
COPY foodcartapp ./foodcartapp
COPY restaurateur ./restaurateur
COPY star_burger ./star_burger
COPY templates ./templates
COPY manage.py ./

RUN git config --global --add safe.directory $HOME

EXPOSE 8000
