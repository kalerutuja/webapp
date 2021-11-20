#!/bin/bash

cd /home/ubuntu/webapp
pkill -f 'python3 main.py'
tee >(logger) <<< "webapp: stopped"
sudo pkill apache2
tee >(logger) <<< "apache2: stopped"
nohup python3 main.py > /dev/null 2>&1 &
tee >(logger) <<< "webapp: started"
sudo systemctl restart amazon-cloudwatch-agent
tee >(logger) <<< "amazon-cloudwatch-agent: restarted"