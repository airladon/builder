# Production environment that can be used directly on Heroku. 
# Differences to stage include:
#  - App files are copied into the container, no volume mounting
#  - Gunicorn is run directly



FROM python:3.7.3-slim

WORKDIR /opt/app


ADD requirements.txt .
RUN pip install --no-cache-dir -q -r requirements.txt



RUN mkdir app
ADD containers/prod/Procfile .
ADD containers/prod/runtime.txt .
ADD containers/prod/wsgi.py .
ADD app/. app/.
RUN mkdir repo
# RUN rm -rf /opt/app/app/static/src

RUN apt-get update && \
	   apt-get -y install git


RUN useradd -m myuser
RUN chown myuser app
RUN chown myuser app/app/app.db
RUN chmod 666 app/app/app.db
USER myuser


CMD gunicorn --bind 0.0.0.0:$PORT wsgi