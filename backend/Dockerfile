FROM python:3

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get install -y cron

RUN mkdir /code
RUN mkdir /code/logs
RUN mkdir /code/data
WORKDIR /code
ADD . /code/

RUN pip3 install -r /code/requirements.txt

RUN touch /code/logs/cron.log

COPY folding-stats-crontab /etc/cron.d/cjob
RUN chmod 0744 /etc/cron.d/cjob
RUN crontab /etc/cron.d/cjob


ENV PYTHONUNBUFFERED 1
#CMD cron -f
ENTRYPOINT ["/bin/sh", "/code/entrypoint.sh"]