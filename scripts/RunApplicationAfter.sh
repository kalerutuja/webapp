#!/bin/bash

cd /home/ubuntu/webapp
pkill -f 'python3 main.py'
tee >(logger) <<< "webapp: stopped"
sudo pkill -f 'http.server'
tee >(logger) <<< "python webserver: stopped"
sudo systemctl restart amazon-cloudwatch-agent
tee >(logger) <<< "amazon-cloudwatch-agent: restarted"