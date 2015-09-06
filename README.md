Wildlife detection
==================

A wildlife detection camera with Raspberry Pi. Either motion sensing based on the video stream (supported by OpenCV) or a PIR can be used to make wildfile images and videos.

Installation
------------

Before you can run the script, two things have to be done:

1. Install the dependencies
2. Enable I2C support

If everything goes well, the above steps are performed by the install.sh script. First download the repository, then run the script as follows:

1. `chmod +x install.sh`
2. `sudo ./install.sh`

Finally, you need to reboot your Raspberry Pi to make sure all new settings are in effect.

After installing all packages (assuming there are no errors) and reboot, test the I2C: `sudo i2cdetect -y 1`. If you have connected your display (Adafruit CharLCD + I2C expander), you should see one address in use (replace 1 by 0 if you have the very first Raspberry Pi B model with 256MD RAM).

Manual Installation
-------------------

Install all the dependencies from the `install.sh` script and hen enable I2C using [this guide](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c).

Usage
-----

TODO
