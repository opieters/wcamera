#!/bin/bash

echo "[INFO] Installing dependencies (Python, OpenCV)"
cd ~
sudo apt-get update
sudo apt-get install python-dev -y # -y installs missing headers
sudo apt-get install libopencv-dev python-opencv python-smbus i2c-tools # open cv + python bindings + i2c x
sudo apt-get install python-pip
sudo pip install RPi.GPIO imutils
echo "Attempting to automatically enable i2c"

if [-f /etc/modprobe.d/raspi-blacklist.conf]; then
    declare -a content=("i2c-bcm2708" "i2c-dev" "blacklist spi-bcm2708" "blacklist i2c-bcm2708" "dtparam=i2c1=on" "dtparam=i2c_arm=on")
    declare -a files=("/etc/modules" "/etc/modules" "/etc/modprobe.d/raspi-blacklist.conf" "/etc/modprobe.d/raspi-blacklist.conf" "/boot/config.txt" "/boot/config.txt")
else
    declare -a content=("i2c-bcm2708" "i2c-dev" "dtparam=i2c1=on" "dtparam=i2c_arm=on")
    declare -a files=("/etc/modules" "/etc/modules" "/boot/config.txt" "/boot/config.txt")
fi

for i in `seq 1 10`;
do
    EXPR="${content[$i]}"
    FILE="${content[$i]}"
    if [! grep -Fxq "$EXPR" $FILE]; then
        sudo cat "$EXPR" >> "$FILE"
    fi
done

echo "[INFO] Downloading Adafruit Char LCD shield software"
rm -rf Adafruit_Python_CharLCD
git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
cd Adafruit_Python_CharLCD
sudo python setup.py install
echo "[INFO] Installed all dependencies"
echo "[INFO] Tried to install I2C, if failed please check README. Please reboot NOW!"
