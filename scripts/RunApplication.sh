#!/bin/bash

cd /home/ubuntu/webapp
nohup python3 main.py > /dev/null 2>&1 &
tee >(logger) <<< "webapp: started"
