#!/usr/bin/env python

#import ConfigParser
#from ConfigParser import SafeConfigParser
from pprint import pprint
import argparse
import requests
import simplejson

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('organization', help='name of GitHub organization', type=str) # Organization Name
subParser = parser.add_subparsers(help='commands', dest='command')

# show: -, team, member, repo, watch, star
showParser = subParser.add_parser('show', help='Show details')
showParser.add_argument()

# create: team, repo
createParser = subParser.add_parser('create', help='Create a new asset')

# add: team2org, member2team, repo2team/team2repo, [watch], [star]
addParser = subParser.add_parser('add', help='Add to an existing asset')

# remove: watch, star, member_from_team, team_from_repo/repo_from_team
removeParser = subParser.add_parser('remove', help='Remove [from] an existing asset')




args = parser.parse_args()
pprint(args)

""" Manage user Requests """
