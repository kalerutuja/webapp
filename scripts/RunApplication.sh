#!/bin/bash

cd /home/ubuntu/webapp
pkill -f 'python3 main.py'
tee >(logger) <<< "apache2: stopped"
sudo pkill apache2
tee >(logger) <<< "apache2: stopped"
nohup python3 main.py > /dev/null 2>&1 &
tee >(logger) <<< "apache2: stopped"
