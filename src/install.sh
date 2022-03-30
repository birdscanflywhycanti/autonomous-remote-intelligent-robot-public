#!/bin/bash

DTB=`pwd`

echo '=== Installing prerequisites ==='
sudo apt-get update
sudo apt-get -y install i2c-tools python-smbus python-gtk2
sudo easy_install pygame

echo '=== Removing I2C devices from the blacklisting ==='
sudo cp /etc/modprobe.d/raspi-blacklist.conf /etc/modprobe.d/raspi-blacklist.conf.old
sudo sed -i 's/^blacklist i2c-bcm2708/#\0    # We need this enabled for I2C add-ons, e.g. ThunderBorg/g' /etc/modprobe.d/raspi-blacklist.conf

echo '=== Adding I2C devices to auto-load at boot time ==='
sudo cp /etc/modules /etc/modules.old
sudo sed -i '/^\s*i2c-dev\s*/d' /etc/modules
sudo sed -i '/^\s*i2c-bcm2708\s*/d' /etc/modules
sudo sed -i '/^#.*ThunderBorg*/d' /etc/modules
sudo bash -c "echo '' >> /etc/modules"
sudo bash -c "echo '# Kernel modules needed for I2C add-ons, e.g. ThunderBorg' >> /etc/modules"
sudo bash -c "echo 'i2c-dev' >> /etc/modules"
sudo bash -c "echo 'i2c-bcm2708' >> /etc/modules"

echo '=== Adding user "pi" to the I2C permissions list ==='
sudo adduser pi i2c

echo '=== Make scripts executable ==='
chmod a+x *.py
chmod a+x *.sh

echo '=== Create a desktop shortcut for the GUI example ==='
TB_SHORTCUT="${HOME}/Desktop/ThunderBorg.desktop"
echo "[Desktop Entry]" > ${TB_SHORTCUT}
echo "Encoding=UTF-8" >> ${TB_SHORTCUT}
echo "Version=1.0" >> ${TB_SHORTCUT}
echo "Type=Application" >> ${TB_SHORTCUT}
echo "Exec=${DTB}/tbGui.py" >> ${TB_SHORTCUT}
echo "Icon=${DTB}/piborg.ico" >> ${TB_SHORTCUT}
echo "Terminal=false" >> ${TB_SHORTCUT}
echo "Name=ThunderBorg Demo GUI" >> ${TB_SHORTCUT}
echo "Comment=ThunderBorg demonstration GUI" >> ${TB_SHORTCUT}
echo "Categories=Application;Development;" >> ${TB_SHORTCUT}

echo '=== Create a desktop shortcut for the LED GUI example ==='
TB_SHORTCUT="${HOME}/Desktop/ThunderBorg-led.desktop"
echo "[Desktop Entry]" > ${TB_SHORTCUT}
echo "Encoding=UTF-8" >> ${TB_SHORTCUT}
echo "Version=1.0" >> ${TB_SHORTCUT}
echo "Type=Application" >> ${TB_SHORTCUT}
echo "Exec=${DTB}/tbLedGui.py" >> ${TB_SHORTCUT}
echo "Icon=${DTB}/piborg.ico" >> ${TB_SHORTCUT}
echo "Terminal=false" >> ${TB_SHORTCUT}
echo "Name=ThunderBorg LED Demo GUI" >> ${TB_SHORTCUT}
echo "Comment=ThunderBorg LED demonstration GUI" >> ${TB_SHORTCUT}
echo "Categories=Application;Development;" >> ${TB_SHORTCUT}

echo '=== Finished ==='
echo ''
echo 'Your Raspberry Pi should now be setup for running ThunderBorg'
echo 'Please restart your Raspberry Pi to ensure the I2C driver is running'
