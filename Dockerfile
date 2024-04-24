FROM python:3.11.4-slim-buster
LABEL maintainer="nikiyorkovich@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN adduser \
    --disabled-password \
    --no-create-home \
    fastapi-user

USER fastapi-user
