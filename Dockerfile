# syntax=docker/dockerfile:1
FROM python:3.10-slim
MAINTAINER Giuseppe De Marco <demarcog83@gmail.com>
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt
COPY . /opt
RUN ls -al .
RUN pip3 install --upgrade pip
RUN pip3 install -e .
RUN pip3 install design-django-theme

# WORKDIR /django-project/
# RUN ls -al .
# RUN python3 manage.py migrate
# RUN python3 manage.py loaddata dumps/example.json
# ENTRYPOINT python3 manage.py runserver 0.0.0.0:8000
