#!/bin/bash
ps -ef |grep run.py|awk '{print $2}' |xargs kill -9
nohup python /home/bqadm/django/za/zabbixtool/run.py &
