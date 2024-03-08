#!/bin/bash

PYTHON=python3.12
DIR=~/git/remote-jupyter-bot/

cd $DIR
source jupyter-bot/bin/activate
$PYTHON -m pip install -r requirements.txt
$PYTHON ./bot.py
