FROM python:3.9.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/opt/starburger
ENV APP_HOME=/opt/starburger/app

RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/staticfiles
RUN mkdir -p $APP_HOME/media

WORKDIR $HOME
COPY .git ./.git

WORKDIR $APP_HOME
COPY ./requirements.txt .

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev git \
    && pip install --upgrade pip setuptools \
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY backend/address ./address
COPY backend/assets ./assets
COPY backend/foodcartapp ./foodcartapp
COPY backend/restaurateur ./restaurateur
COPY backend/star_burger ./star_burger
COPY backend/templates ./templates
COPY backend/manage.py ./

RUN git config --global --add safe.directory $HOME

EXPOSE 8000
