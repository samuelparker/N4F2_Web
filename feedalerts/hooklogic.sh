#!/bin/bash

cd /code

python manage.py fetchhooklogic

DATE=`date`

echo "Hooklogic job ran at $DATE$" >> /etc/hlcronjob-log.txt