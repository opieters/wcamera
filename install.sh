#!/bin/bash

echo "[INFO] Installing dependencies (Python, OpenCV)"
cd ~
sudo apt-get update
sudo apt-get install python-dev -y # -y installs missing headers
sudo apt-get install libopencv-dev python-opencv python-smbus i2c-tools # open cv + python bindings + i2c x
sudo apt-get install python-pip
sudo pip install RPi.GPIO
echo "[INFO] Downloading Adafruit Char LCD shield software"
rm -rf Adafruit_Python_CharLCD
git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
cd Adafruit_Python_CharLCD
sudo python setup.py install
echo "[INFO] Installed all dependencies"
echo "[INFO] Make sure I2C is installed"
