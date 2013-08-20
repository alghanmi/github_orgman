#!/usr/bin/env python

import argparse
import githubclient

#import ConfigParser
#from ConfigParser import SafeConfigParser
from pprint import pprint


# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('organization', help='name of GitHub organization', type=str) # Organization Name
subParser = parser.add_subparsers(help='commands', dest='command')

# show: -, team, member, repo
showParser = subParser.add_parser('show', help='Show details')
showParser.add_argument("-t", "--team", help="show team(s) information", metavar="team_id", nargs="*", dest="show_teamid")
showParser.add_argument("-m", "--member", help="show member(s) information", metavar="member", nargs="*", dest="show_member")
showParser.add_argument("-r", "--repo", help="show repo(s) information", metavar="repo", nargs="*", dest="show_repo")

# create: team, repo
createParser = subParser.add_parser('create', help='Create a new asset')

# add: team2org, member2team, repo2team/team2repo, milestone+repo, issue+repo
addParser = subParser.add_parser('add', help='Add to an existing asset')

# remove: member_from_team, team_from_repo/repo_from_team
removeParser = subParser.add_parser('remove', help='Remove [from] an existing asset')

# subscribe: repo
removeParser = subParser.add_parser('sub', help='Subscribe to (a) repo(s)')

# unsubscribe: repo
removeParser = subParser.add_parser('unsub', help='unsubscribe from (a) repo(s)')



githubclient.github_get_request('abc')

args = parser.parse_args()
pprint(args)

""" Manage user Requests """
