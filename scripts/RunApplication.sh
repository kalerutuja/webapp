#!/bin/bash

PyPID=`/usr/bin/ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}'`
cd /home/ubuntu/webapp
if [ $PyPID ]; then
    echo $PyPID
    kill -n 15 $PyPID
fi
sudo pkill apache2
nohup python3 main.py > /dev/null 2>&1 &
