#!/usr/bin/env bash

printenv | cat - /etc/cron.d/cjob > /app/cjob.tmp \
    && mv /app/cjob.tmp /etc/cron.d/cjob

chmod 744 /etc/cron.d/cjob

tail -f /app/logs/cron.log &

python3 /app/folding-stats.py
/app/webservice.sh &

cron -f
