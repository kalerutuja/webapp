#!/bin/bash

PyPID=`/usr/bin/ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}'`
if [ $PyPID ]; then
    echo $PyPID
    kill -n 15 $PyPID
fi
sudo service apache2 stop
sudo apt-get purge apache2 apache2-utils apache2.2-bin apache2-common
sudo apt-get autoremove
sudo rm -rf /etc/apache2
