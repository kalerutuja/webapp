#!/bin/bash

PyPID=`/usr/bin/ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}'`
if [ $PyPID ]; then
    echo $PyPID
    kill -n 15 $PyPID
    sudo pkill apache2
fi
sudo systemctl stop amazon-cloudwatch-agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:cloudwatch-config.json \
    -s
sudo systemctl start amazon-cloudwatch-agent
