Wildlife detection
==================

A wildlife detection camera with Raspberry Pi. Either motion sensing based on the video stream (supported by OpenCV) or a PIR can be used to make wildlife images and videos.

Hardware
--------

Hardware (yes, some of it has newer and better versions) that is used to test this project:

* [character LCD display](https://www.adafruit.com/products/772)
* [wifi dongle](http://www.edimax.com/edimax/merchandise/merchandise_detail/data/edimax/global/wireless_adapters_n150/ew-7811un)
* [Raspberry Pi](https://www.raspberrypi.org/products/model-b/)
* [PIR sensor](https://www.adafruit.com/products/189)
* [NoIR camera](https://www.raspberrypi.org/products/pi-noir-camera/)

Installation
------------

### Precompiled OpenCV (recommended)

Before you can run the script, two things have to be done:

1. Install the dependencies
2. Enable I2C support

The above steps are performed by the `install.sh` script. First clone the repository, then run the script:

1. `git clone https://github.com/opieters/wcamera`
1. `chmod +x install.sh`
2. `sudo ./install.sh`

Finally, you need to reboot your Raspberry Pi to make sure all new settings are in effect.

After installing all packages (assuming there are no errors) and reboot, test the I2C: `sudo i2cdetect -y 1`. If you have connected your display (Adafruit CharLCD + I2C expander), you should see one address in use (replace 1 by 0 if you have the very first Raspberry Pi B model with 256MB RAM).

### Compile OpenCV on the Raspberry Pi (advanced)

Users who want to compile OpenCV themselves, should run the `install2.sh` script with is based on [this tutorial](http://www.pyimagesearch.com/2015/02/23/install-opencv-and-python-on-your-raspberry-pi-2-and-b/) but otherwise performs the same actions. Please mind that OpenCV is installed in a `virtualenv` for convenience.

### I2C failed to Install

Open `raspi-config`, select Advanced Options (9) and enable I2C. Alternatively, use [this guide](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c).

### Camera

Before attempting to record anything, make sure you activated the camera in `raspi-config` and correctly connected the camera module to the Raspberry Pi board.

### Hotspot (Access Point Mode)

Setup access point mode using [this guide](http://elinux.org/RPI-Wireless-Hotspot), but do not apply the _at boot_ settings. These will be performed by the script.

If you are using the EDIMAX wifi dongle, update Hostapd with the version in [this guide](http://www.daveconroy.com/turn-your-raspberry-pi-into-a-wifi-hotspot-with-edimax-nano-usb-ew-7811un-rtl8188cus-chipset/) (you can skip everything else in this guide). Be sure to chance the driver settings in the `/etc/hostapd/hostapd.conf` file to `driver=rtl871xdrv`. Otherwise this will not work.

Usage
-----

Run the script using `python wcamera.py` and use the provided UI on the character LCD and mobile UI.

FAQ
---

### Why only Python2.7?

Currently, OpenCV 2 is used, which does not officially support Python3. Moving towards OpenCV 3 will resolve this issue, but OpenCV 3 is still very new and thus OpenCV 2 was preferred.

License
-------

© 2015-2016 Olivier Pieters, MIT license.
