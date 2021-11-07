#!/bin/bash

PyPID=ps ax | grep 'python3 main.py' | grep -v grep | awk '{print $1}'
cd /home/ubuntu/webapp
if [ PyPID ] then
    kill pyPID
fi
python3 main.py &

