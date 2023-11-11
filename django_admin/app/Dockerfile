FROM python:3.8

WORKDIR /opt/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'
ENV PIP_ROOT_USER_ACTION=ignore


RUN groupadd -r django && useradd -d /opt/app -r -g django django \
    && chown django:django -R /opt/app/

COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN apt-get update && apt-get install netcat-traditional && python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . .

RUN chmod +x docker-entrypoint.sh  && mkdir /opt/app/static


EXPOSE 8000

VOLUME /opt/app/static
RUN chown -R django:django /opt/app/static

USER django
ENTRYPOINT ["/opt/app/docker-entrypoint.sh"]