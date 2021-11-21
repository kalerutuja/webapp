#!/bin/bash

sudo systemctl stop amazon-cloudwatch-agent
tee >(logger) <<< "amazon-cloudwatch-agent: stopped"
sudo mv cloudwatch-config.json /home/ubuntu/
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/home/ubuntu/cloudwatch-config.json \
    -s
sudo systemctl start amazon-cloudwatch-agent
tee >(logger) <<< "amazon-cloudwatch-agent: started"