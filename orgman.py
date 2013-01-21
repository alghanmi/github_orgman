#!/usr/bin/env python

from ConfigParser import SafeConfigParser
from pprint import pprint
import argparse
import requests
import simplejson

def gitHubRequest(url):
	""" Return a dict with the result of this request """
	r = requests.get(url, auth=(githubUsername, githubPassword))
	if r.status_code == 200:
		res = simplejson.loads(r.content)
		#pprint(res)
		return res
	else:
		print "[ERROR] Bad Request. Status Code", r.status_code
		return None

def getOrgInfo(orgName):
	""" Lookup Organization Information """
	res = gitHubRequest("https://api.github.com/orgs/{}".format(orgName))
	
	if res != None:
		print "Organization URL :", res["html_url"]
		print "Organization ID  :", res["id"]
		print "No. Public Repos :", res["public_repos"]
		print "No. Private Repos:", res["owned_private_repos"]

def printMembers(memberResultSet):
	""" Print list of members given a result set """
	memberCount = len(memberResultSet)
	memberCounter = 0
	for m in memberResultSet:
		memberCounter += 1
		print "\t\t{}. [{:7}] {}".format(str(memberCounter).zfill(len(str(memberCount))), m["id"], m["login"])

def listOrgTeams(orgName, listMembers):
	""" List Organization Teams and optionally their members """
	res = gitHubRequest("https://api.github.com/orgs/{}/teams".format(orgName))
	
	if res != None:		
		teamCount = 0
		for r in res:
			teamCount += 1
			
			print "{}. Team {}: {}.".format(teamCount, r["id"], r["name"])
			if listMembers:
				teamMemberCount = -1
				teamRes = gitHubRequest("https://api.github.com/teams/{}".format(r["id"]))
				teamMemberCount = teamRes["members_count"]
				print "\t{} Members with {} repo(s)".format(teamRes["members_count"], teamRes["repos_count"])
				
				memberRes = gitHubRequest("https://api.github.com/teams/{}/members".format(r["id"]))
				printMembers(memberRes)
				
	else:
		print "[INFO] No teams exist"

def listOrgMembers(orgName):
	""" List Organization Members """
	res = gitHubRequest("https://api.github.com/orgs/{}/members".format(orgName))
	printMembers(res)

"""
   Obtain GitHub username & password from config file
"""
parser = SafeConfigParser()
parser.read("orgman.conf")

githubUsername = parser.get("github", "username")
githubPassword = parser.get("github", "password")

"""
    Get commandline arguments
"""
parser = argparse.ArgumentParser()
parser.add_argument("org", help="name of GitHub organization", type=str) # Organization Name
parser.add_argument("-l", "--list", help="option to list details of specified field such as org, team or member", action="store_true")
parser.add_argument("-t", "--team", "--teams", help="perform operations on teams teams", action="store_true")
parser.add_argument("-m", "--member", "--members", help="perform operations on members", action="store_true")

args = parser.parse_args()

"""
    GitHub API request
"""

if args.list and args.team:
	listOrgTeams(args.org, args.member)

elif args.list and args.member and (not args.team):
	listOrgMembers(args.org)

else:
	getOrgInfo(args.org)
