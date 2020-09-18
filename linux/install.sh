#! /bin/bash

##Raisensu Installation Script

#Make /opt/Raisensu directory
mkdir /opt/Raisensu

#Move Raisensu files to /usr/local/bin
cp ../../Raisensu /opt/

#Copy raisensu_monitor.serivce file to /lib/systemd/system/
cp raisensu_monitor.service /lib/systemd/system/raisensu_monitor.service

#Change permissions for raisensu_monitor.serivce file
chmod 644 /lib/systemd/system/raisensu_monitor.service

#Restart systemd daemon
systemctl daemon-reload

#Start raisensu_monitor.service
systemctl start raisensu_monitor.service

#Enable raisensu_monitor.service to start at start-up
systemctl enable raisensu_monitor.service
