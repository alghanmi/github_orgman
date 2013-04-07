# GitHub Organization Manager
A collection of commandline-based tools used to help organize [GitHub organizations](https://github.com/blog/674-introducing-organizations). Although the web interface works well for basic management, in a number of settings (e.g. GitHub-based courses) you would require bulk operations. This is a work in progress. Basic help could be viewed by:
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

## Sample Usage Scenarios
### Adding Members to Organization
Members should be [GitHub](https://github.com/signup/free) users and they need to be added to a team in order to be members of organization. Start by creating a `TEAM_NAME` team:
```shell
python orgman.py ORG_NAME add --team TEAM_NAME
```

GitHub uses id numbers for all its teams. For usability, `orgman` creates an ini-style organization profile file to lookup such information. if you created a profile beforehand, you can simply use that one.
```shell
python orgman.py ORG_NAME add --team TEAM_NAME --memeber GITHUB_USERNAME
```
or
```shell
python orgman.py ORG_NAME add --profile ORG_NAME.profile --team TEAM_NAME -memeber GITHUB_USERNAME
```

Adding milestone to repo and assigne it to a user and give it a label
```shell
python orgman.py ORG_NAME add --repo REPO_NAME --member GITHUB_USERNAME --issues ISSUES_FILE
```
