#!/bin/bash

PyPID=`/usr/bin/ps aux | grep "main.py" | grep -v grep | awk '{print $2}'`
if [ $PyPID ]; then
    echo $PyPID
    kill -n 15 $PyPID
fi
sudo systemctl stop amazon-cloudwatch-agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/home/ubuntu/cloudwatch-config.json \
    -s
sudo systemctl start amazon-cloudwatch-agent
