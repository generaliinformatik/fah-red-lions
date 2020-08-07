FROM python:3

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get install -y cron

RUN mkdir /app
RUN mkdir /app/logs
RUN mkdir /app/data
WORKDIR /app
ADD ./app/ /app/

RUN pip3 install -r /app/requirements.txt

RUN touch /app/logs/cron.log

COPY ./app/folding-stats-crontab /etc/cron.d/cjob
RUN chmod 0744 /etc/cron.d/cjob
RUN crontab /etc/cron.d/cjob


ENV PYTHONUNBUFFERED 1
#CMD cron -f

EXPOSE 8888

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
