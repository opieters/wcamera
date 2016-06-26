pushd ~

# Based on these instructions: http://www.pyimagesearch.com/2015/02/23/install-opencv-and-python-on-your-raspberry-pi-2-and-b/

echo "Updating repos and current dependencies..."
sudo apt-get update
sudo apt-get upgrade
sudo rpi-update

echo "Installing essential tools"
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt-get install libgtk2.0-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libatlas-base-dev gfortran

echo "Installing Python"
sudo apt-get install python2.7-dev python-pip

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

popd

echo "All done."
