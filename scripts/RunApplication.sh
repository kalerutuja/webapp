#!/bin/bash

PyPID=`/usr/bin/ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}'`
cd /home/ubuntu/webapp
if [ $PyPID ]; then
    echo $PyPID
    kill -n 15 $PyPID
fi
python3 main.py &