#!/bin/bash

cd /home/ubuntu/webapp
pkill -f 'python3 main.py'
sudo pkill apache2
nohup python3 main.py > /dev/null 2>&1 &
sudo systemctl restart amazon-cloudwatch-agent
