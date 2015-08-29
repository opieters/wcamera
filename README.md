Wildlife detection
==================

A Raspberry Pi + Camera module are used to record video an perform (basic) motion ditection on this video. The project is Python based and requires OpenCV to be installed on your system.

Installation
------------

1. Update `apt-get`: `sudo apt-get update`
2. Install OpenCV + Python bindings: `sudo apt-get install libopencv-dev python-opencv`.
3. Install project

For use of the motion detector
1. sudo apt-get update
2. enable i2c support ([guide](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c))
3. sudo pip install RPi.GPIO
4. install Adafruit deps:
    * git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
    * cd Adafruit_Python_CharLCD
    * sudo python setup.py install

Usage
-----
