#!/bin/bash

cd ~
sudo apt-get update
sudo apt-get install libopencv-dev python-opencv
sudo pip install RPi.GPIO
git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
cd Adafruit_Python_CharLCD
sudo python setup.py install
