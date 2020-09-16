![BuildStatus](https://img.shields.io/badge/build-success-brightgreen)  [![Codacy Badge](https://api.codacy.com/project/badge/Grade/d01dd77641f1470ba362255f9c7d7a58)](https://app.codacy.com/manual/cjh30/Raisensu?utm_source=github.com&utm_medium=referral&utm_content=schnipdip/Raisensu&utm_campaign=Badge_Grade_Dashboard) [![Known Vulnerabilities](https://snyk.io/test/github/schnipdip/Raisensu/badge.svg)](https://snyk.io/test/github/schnipdip/Raisensu) 
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/schnipdip/Raisensu.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/schnipdip/Raisensu/context:python) [![Total alerts](https://img.shields.io/lgtm/alerts/g/schnipdip/Raisensu.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/schnipdip/Raisensu/alerts/)

![reisensu_img](https://funkyimg.com/i/373GZ.png)

A simple license asset management tool.

# Key Features

Supports license encryption.

Supports license expiration SMTP notifications.

Supports license expiration logs.

Supports license expiration monitoring service.

Supports Sqlite3 and Postgres.


# Get Started

1. Install requirements `pip3 install -r requirements.txt`
1. Generate Encryption Key `python generate_key.py`
1. Build the database table `python raisensu.py -t`

# Possible Arguments
```
optional arguments:

  -h, --help   show this help message and exit
  
  -c           Parse through import.csv file
  
  -d           Delete Asset
  
  --delete_all  Delete all records in table
  
  -t           Create a New Table if it has not been created already
  
  -v           View all entries
  
  -u           Update an entry
  
  -n NAME      Name of the License Product
  
  -a HOSTNAME  Name of the hostname the license is attached to
  
  -l LICENSE   License data
  
  -q QUANTITY  Total Number of licenses
  
  -x EXPIRE    License expiration date [requires .csv file]
  
  -e EXPORT    Export SQL Database to CSV file
  
  -s ENVIRONMENT Environment the license resides in
  
  -r DESCRIPTION Description of the license
```
# Examples

1. Getting help: `python raisensu.py -h`
2a. Adding a new asset from command-line: `python raisensu.py -n 'Product Name' -l 'xopi08infsdfpoi3409c' -q 10 -x 12/31/2021` (`-a` is optional to add a host)
2b. Adding a new asset from command-line:  `python raisensu.py -n 'Product Name' -l 'xopi08infsdfpoi3409c' -q 1 -x 12/31/2021 -a Host01 -s 'Dev' -r 'License for Host01 in Dev' `

![example1](https://funkyimg.com/i/373Jh.png)

3. Import a list of assets from the import.csv file: `python raisensu.py -c`
4. Update an asset: `python raisensu.py -u` - _follow the steps_
5. View all assets in the database: `python raisensu.py -v`
6. Export assets to a .csv file: `python raisensu.py -e [location]`

# Output
![reisensu_img](https://funkyimg.com/i/373JH.png)

# Configure Monitoring (optional)

1. (Windows) Set up a Task Schedule for `raisensu_monitor.py`
2. (Linux) Set up a Linux CronJob for `raisensu_monitor.py`
3. Edit the `monitor_settings.ini` file with the appropriate configuration information that fits your environment

# Troubleshooting

1. (Linux) If you are having trouble with `generate_key.py`, issue the following command: `dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64 > secret.key`

## TODO:

- Select NAME output
- Support Remote Database
- Query and return Hostname
