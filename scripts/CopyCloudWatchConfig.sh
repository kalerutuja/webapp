#!/bin/bash

pkill -f 'python3 main.py'
tee >(logger) <<< "webapp: stopped"
sudo systemctl stop amazon-cloudwatch-agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/home/ubuntu/cloudwatch-config.json \
    -s
sudo systemctl start amazon-cloudwatch-agent
tee >(logger) <<< "amazon-cloudwatch-agent: started"