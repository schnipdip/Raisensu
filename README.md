![BuildStatus](https://img.shields.io/badge/build-success-brightgreen)

![reisensu_img](https://funkyimg.com/i/373GZ.png)

A simple license asset management tool.


# Get Started

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d01dd77641f1470ba362255f9c7d7a58)](https://app.codacy.com/manual/cjh30/Raisensu?utm_source=github.com&utm_medium=referral&utm_content=schnipdip/Raisensu&utm_campaign=Badge_Grade_Dashboard)

1. Install requirements `pip3 install requirements.txt`
1. Generate Encryption Key `python generate_key.py`
1. Build the database table `python raisensu.py -t`

# Examples

1. Getting help: `python raisensu.py -h`
2. Adding a new asset from command-line: `python raisensu.py -n 'Product Name' -l 'xopi08infsdfpoi3409c' -q 10` (`-a` is optional to add a host)

![example1](https://funkyimg.com/i/373Jh.png)

3. Import a list of assets from the import.csv file: `python raisensu.py -c`
4. Update an asset: `python raisensu.py -u` - _follow the steps_
5. View all assets in the database: `python raisensu.py -v`

# Output
![reisensu_img](https://funkyimg.com/i/373JH.png)

## TODO:

- Delete all assets
- Export database to CSV
- Select NAME output
