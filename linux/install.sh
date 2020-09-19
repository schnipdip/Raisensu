#! /bin/bash

##Raisensu Installation Script

#Make /opt/Raisensu directory
mkdir /opt/Raisensu

#Move Raisensu files to /usr/local/bin
cp -R ../../Raisensu /opt/

#Copy raisensu_monitor.serivce file to /lib/systemd/system/
cp raisensu_monitor.service /lib/systemd/system/raisensu_monitor.service

#Change permissions for raisensu_monitor.serivce file
chmod 644 /lib/systemd/system/raisensu_monitor.service

#Restart systemd daemon
systemctl daemon-reload

#Remove Raisensu/windows directory
rm -r /opt/Raisensu/windows

#Echo new access location
echo "Raisensu has been installed in /opt/Raisensu"
echo ""
echo "Change Directories to /opt/Raisensu/linux/"
echo ""
echo "Perform the following steps in this order:"
echo "sudo python3 generate_key.py"
echo "sudo python3 raisensu.py -t"
echo "sudo systemctl start raisensu_monitor.service"
echo "sudo systemctl enable raisensu_monitor.service"
