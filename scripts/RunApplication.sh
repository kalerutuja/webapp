#!/bin/bash

PyPID=`/usr/bin/ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}'`
cd /home/ubuntu/webapp
pkill -f 'python3 main.py'
echo -e 'webapp: stopped'
sudo pkill apache2
echo -e 'apache2: stopped'
nohup python3 main.py > /dev/null 2>&1 &
echo -e 'webapp: started'