cd Desktop
mkdir Autexys
mkdir Autexys/AutexysData
git clone http://github.com/stevennoyce/AutexysHost

sudo apt-get update
pip3 install matplotlib
pip3 install scipy
sudo apt-get install libatlas3-base
pip3 install pyvisa
pip3 install pyvisa-py

# Set chromium as default browser by opening it
# Set password to be autexys1

# Install Resilio Sync
## Instructions at https://help.resilio.com/hc/en-us/articles/206178924-Installing-Sync-package-on-Linux
echo "deb http://linux-packages.resilio.com/resilio-sync/deb resilio-sync non-free" | sudo tee /etc/apt/sources.list.d/resilio-sync.list
wget -qO - https://linux-packages.resilio.com/resilio-sync/key.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install resilio-sync
sudo systemctl enable resilio-sync
# use id command to find the user that 'pi' should be replaced with
sudo usermod -aG pi rslsync
sudo chmod g+rw synced_folder
# Visit sync ui at localhost:8888
# Set resilio username as pi and password as autexys1
# Resilio diplay name for sharing can be rpi1 or similar

pip3 install psutil
pip3 install flask-socketio
pip3 install gevent
pip3 install lmfit


wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
bash Miniconda3-latest-Linux-armv7l.sh
conda config --add channels rpi
conda install python=3.6
conda create --name py36 python=3.6
source activate py36


