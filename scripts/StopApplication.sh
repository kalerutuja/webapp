#!/bin/bash

PyPID=`/usr/bin/ps aux | grep "main.py" | grep -v grep | awk '{print $2}'`
if [ $PyPID ]; then
    echo $PyPID
    kill -n 15 $PyPID
fi