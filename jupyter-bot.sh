#!/bin/bash

DIR=~/git/remote-jupyter-bot/

cd $DIR
source jupyter-bot/bin/activate
python3.12 -m pip install -r requirements.txt
python3.12 ./bot.py
