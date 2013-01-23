# GitHub Organization Manager
A collection of commandline-based tools used to help organize [GitHub organizations](https://github.com/blog/674-introducing-organizations). Although the web interface works well for basic management, in a number of settings (e.g. GitHub-based projects in an academic setting) you would require bulk operations that the web interface will be very tedious.

This is a work in progress. 

### Installation
This application takes advantage of the `requests` and `simplejson` modules. You would need to install them if they are not on your system:

```shell
pip install requests
pip install simplejson
```

- Create a configuration file from the provided sample

```shell
cp orgman.conf.default orgman.conf
```

- Edit `orgman.conf` to include your GitHub username and password

## Usage
Basic usage instructions are available:
```shell
python orgman.py --help
```