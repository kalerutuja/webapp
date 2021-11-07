#!/bin/bash

PyPID=`/usr/bin/ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}'`
if [ $PyPID ]; then
    kill -n 15 $pyPID
fi

kill -n 15 $pyPID