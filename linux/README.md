After cloning the Raisensu repository, navigate to:

`Raisensu/linux`

In order to provision Raisensu properly, issue the following command with suder privileges:

`sudo sh install.sh`

Lastly, follow along with the end requirements that the install.sh provides.


To get started with Raisensu, navigate to /opt/Raisensu/linux.

Issue the following command to generate an encryption key:

`sudo python3 generate_key.py`

Next, modify the settings files:

`database_settings.ini`
`monitor_settings.ini`

After, issue the following command to create your database table:

`sudo python3 raisensu.py -t`

Now you have fully provisioned Raisensu and you can start adding and managing license assets.
