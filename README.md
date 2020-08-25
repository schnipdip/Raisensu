![BuildStatus](https://img.shields.io/badge/Success-Working-brightgreen)

![reisensu_img](https://funkyimg.com/i/373GZ.png)

A simple license asset management tool.


# Get Started

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

- Implement encryption to protect licenses
- Delete all assets
