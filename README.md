# GitHub Organization Manager
A collection of commandline-based tools used to help organize [GitHub organizations](https://github.com/blog/674-introducing-organizations). This is a work in progress. Basic help could be viewed by:
```shell
python orgman.py --help
```

GitHub username and password should be listed in the `orgman.conf`.

### Installation
- Install [pip](http://pypi.python.org/pypi/pip) if it is not available
```shell
sudo apt-get install python-pip
pip install requests
```
- Create the configuration file from default version
```shell
cp orgman.conf.default orgman.conf
```
- Edit `orgman.conf`
