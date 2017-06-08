#!/bin/bash
ps -ef |grep run.py|awk '{print $2}' |xargs kill -9
nohup python /home/bqadm/django/za/zabbixtool/run.py &
nohup python /home/bqadm/django/fullscreen/manage.py runserver 0.0.0.0:8000 &
nohup python /home/bqadm/django/hotline/manage.py runserver 0.0.0.0:8000 &
