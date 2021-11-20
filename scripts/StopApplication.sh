#!/bin/bash

pkill -f 'python3 main.py'
tee >(logger) <<< "apache2: stopped"