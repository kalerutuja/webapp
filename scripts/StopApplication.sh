#!/bin/bash

PyPID=ps ax | grep 'python3 main.py' | grep -v grep | awk '{print $1}'
if [ PyPID ] then
    kill pyPID
fi
kill pyPID
