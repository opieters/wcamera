pushd ~

# Based on these instructions: http://www.pyimagesearch.com/2015/02/23/install-opencv-and-python-on-your-raspberry-pi-2-and-b/

echo "Updating repos and current dependencies..."
sudo apt-get update
sudo apt-get upgrade
sudo rpi-update

echo "Installing essential tools"
sudo apt-get -y install build-essential cmake pkg-config
sudo apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt-get -y install libgtk2.0-dev
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get -y install libatlas-base-dev gfortran

echo "Installing Python"
sudo apt-get -y install python2.7-dev python-pip

echo "Installing Virtualenv"
sudo pip install virtualenv virtualenvwrapper
sudo rm -rf ~/.cache/pip

echo 'export WORKON_HOME=$HOME/.virtualenvs' >> ~/.profile
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.profile

echo "Setting up Virtualenv"
source ~/.profile
mkvirtualenv cv

echo "Installing Python dependencies"
pip install numpy

echo "Downloading OpenCV2"
wget -O opencv-2.4.13.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.13/opencv-2.4.13.zip/download
unzip opencv-2.4.13.zip
cd opencv-2.4.13

echo "Building OpenCV"
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON  -D BUILD_EXAMPLES=ON ..

make
sudo make install
sudo ldconfig

echo "Symlinking..."
cd ~/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
ln -s /usr/local/lib/python2.7/site-packages/cv.py cv.py

echo "Installing other dependencies for wcamera..."

sudo apt-get update
sudo apt-get -y install ruby ruby-dev python-dev -y # -y installs missing headers
sudo apt-get -y install python-smbus i2c-tools rubygems libmagickwand-dev python-picamera # open cv + python bindings + i2c x
sudo pip install RPi.GPIO imutils picamera wifi Wand PyYAML
sudo gem install jekyll

echo "Attempting to automatically enable i2c"

if [ -f /etc/modprobe.d/raspi-blacklist.conf ]; then
    declare -a content=("i2c-bcm2708" "i2c-dev" "blacklist spi-bcm2708" "blacklist i2c-bcm2708" "dtparam=i2c1=on" "dtparam=i2c_arm=on")
    declare -a files=("/etc/modules" "/etc/modules" "/etc/modprobe.d/raspi-blacklist.conf" "/etc/modprobe.d/raspi-blacklist.conf" "/boot/config.txt" "/boot/config.txt")
else
    declare -a content=("i2c-bcm2708" "i2c-dev" "dtparam=i2c1=on" "dtparam=i2c_arm=on")
    declare -a files=("/etc/modules" "/etc/modules" "/boot/config.txt" "/boot/config.txt")
fi

echo "[INFO] Downloading Adafruit Char LCD shield software"
rm -rf Adafruit_Python_CharLCD
git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
cd Adafruit_Python_CharLCD
sudo python setup.py install
echo "[INFO] Installed all dependencies"
echo "[INFO] Tried to install I2C, if failed please check README. Please reboot NOW!"

popd

pushd ./server
bower install
popd

echo "All done."
