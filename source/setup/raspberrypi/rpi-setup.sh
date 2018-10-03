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
