#! /bin/bash

##Raisensu Installation Script

#Make /opt/Raisensu directory
mkdir /opt/Raisensu

#Move Raisensu files to /usr/local/bin
cp -R ../../Raisensu /opt/
echo "Moved Raisensu to /opt/Raisensu"

#Copy raisensu_monitor.serivce file to /lib/systemd/system/
cp raisensu_monitor.service /lib/systemd/system/raisensu_monitor.service
echo "Copied the raisensu_monitor.service to systemd"

#Change permissions for raisensu_monitor.serivce file
chmod 644 /lib/systemd/system/raisensu_monitor.service
echo "Modified the permissions on raisensu_monitor.service"

#Copy raisensu_timer.serivce file to /lib/systemd/system/
cp raisensu_timer.service /lib/systemd/system/raisensu_timer.service
echo "Copied the raisensu_timer.service to systemd"

#Change permissions for raisensu_timer.serivce file
chmod 644 /lib/systemd/system/raisensu_timer.service
echo "Modified the permissions on raisensu_timer.service"

#Restart systemd daemon
echo "Restarting systemd daemon"
systemctl daemon-reload
echo "Systemd daemon reloaded"

#Start raisensu_timer.service
systemctl start raisensu_timer.service

#Enable raisensu_timer.service at start
systemctl enable raisensu_timer.service

#Remove Raisensu/windows directory
rm -r /opt/Raisensu/windows
echo "Removed /opt/Raisensu/windows directory"

#Echo new access location
echo ""
echo ""
echo "Raisensu has been installed in /opt/Raisensu"
echo ""
echo "Change Directories to /opt/Raisensu/linux/"
echo ""
echo "Perform the following steps in this order:"
echo "sudo python3 generate_key.py"
echo "sudo python3 raisensu.py -t"
echo "sudo systemctl start raisensu_monitor.service"
echo "sudo systemctl enable raisensu_monitor.service"
