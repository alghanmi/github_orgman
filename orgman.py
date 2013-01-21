#!/usr/bin/env python

from ConfigParser import SafeConfigParser
from pprint import pprint
import argparse
import requests
import simplejson

def unsupportedFeature(feature):
	print "The following feature is not yet supported {}".format(feature)
	exit(2)

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
	pprint(res)
	if res != None:
		print "Organization URL :", res["html_url"]
		print "Organization ID  :", res["id"]
		print "No. Public Repos :", res["public_repos"]
		print "No. Private Repos:", res["owned_private_repos"]

def generateOrgPofile(orgName):
	""" Generate Organization Profile """
	orgRes = gitHubRequest("https://api.github.com/orgs/{}".format(orgName))
	if orgRes != None:
		# Org info
		print "[github_org]"
		print "name = {}".format(orgRes["login"])
		print "id = {}".format(orgRes["id"])
		print "url = {}".format(orgRes["html_url"])
		print ""
		# Team info
		print "[org_teams]"
		teamRes = gitHubRequest("https://api.github.com/orgs/{}/teams".format(orgName))
		for t in teamRes:
			print "{} = {}".format(t["name"], t["id"])
		print ""
		# Member info
		print "[org_members]"
		memberRes = gitHubRequest("https://api.github.com/orgs/{}/members".format(orgName))
		for m in memberRes:
			print "{} = {}".format(m["login"], m["id"])
	

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
subParser = parser.add_subparsers(help="commands")

# List Commands
listParser = subParser.add_parser("list", help="List details of specified attribute")
listParser.add_argument("-p", "--profile", help="generate an organization/team profile", action="store_true", dest="listProfile")
listParser.add_argument("-t", "--team", help="list team(s)", metavar="team_id", nargs="*", dest="listTeamID")
listParser.add_argument("-m", "--member", help="list member(s)", metavar="member_id", nargs="*", dest="listMemberID")

# Add Commands
#addParser = subParser.add_parser("add", help="Add resources to specified organization")
#addParser.add_argument("-t", "--team", "--teams", help="perform operations on teams teams", action="append", dest='teamArgs', default=[])
#addParser.add_argument("-m", "--member", "--members", help="perform operations on members", action="append", dest='memberArgs', default=[])

args = parser.parse_args()
#pprint(args)

"""
    Manage user Requests
"""
# list --profile
if args.listProfile:
	# Generate complete organization profile
	if args.listTeamID == None and args.listMemberID == None:
		generateOrgPofile(args.org)
	# Generate team profile
	elif args.listTeamID != None and args.listMemberID == None:
		print "team profile"
	# Generate member profile
	elif args.listTeamID == None and args.listMemberID != None:
		print "member profile"
	# Generate a member's profile within a team
	else:
		unsupportedFeature("A member's pofile within a team")
	
		

# list --team
elif args.listTeamID != None:
	# list --team (no team specificed)
	if len(args.listTeamID) == 0:
		# list --team --member (all team with members)
		if args.listMemberID != None and len(args.listMemberID) == 0:
			listOrgTeams(args.org, True)
		# list --team --member member1 [member2 ...]
		elif args.listMemberID != None and len(args.listMemberID) > 0:
			unsupportedFeature("You can not specify members when listing multiple teams")
		# list --team (list teams without members)
		else:
			listOrgTeams(args.org, False)
	# list --team team1 [team2 ..] [--member]
	else:
		unsupportedFeature("listings involving one or more teams")

# list --member (no teams specified)
elif args.listMemberID != None:
	# list --member (all members)
	if len(args.listMemberID) == 0:
		listOrgMembers(args.org)
	else:
		unsupportedFeature("listings involving more than one team member")

# no-option specified
else:
	getOrgInfo(args.org)
""" # """
