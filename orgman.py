#!/usr/bin/env python

import ConfigParser
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

def gitHubPost(url, payload):
	""" Send a POST request to GitHub via API """
	r = requests.post(url, data=simplejson.dumps(payload), auth=(githubUsername, githubPassword))
	res = simplejson.loads(r.content)
	#pprint(res)
	if r.status_code == 201:
		return res
	else:
		details = ""
		for e in res["errors"]:
			details += "{}.{}: {}.".format(e["resource"], e["field"], e["code"])
		print "[ERROR][HTTP {}] {} - {}".format(r.status_code, res["message"], details)
		return None

def gitHubPut(url):
	""" Send a PUT request to GitHub via API """
	# http://developer.github.com/v3/orgs/teams/#add-team-member
	r = requests.put(url, auth=(githubUsername, githubPassword))
	if r.status_code == 204:
		return True
	else:
		res = simplejson.loads(r.content)
		pprint(res)
		details = ""
		if "errors" in res:
			for e in res["errors"]:
				details += "{}.{}: {}.".format(e["resource"], e["field"], e["code"])
		print "[ERROR][HTTP {}] {} - {}".format(r.status_code, res["message"], details)
		return False

def getGitHubUserInfo(username):
	""" Lookup Organization Information """
	res = gitHubRequest("https://api.github.com/users/{}".format(username))
	#pprint(res)
	if res != None:
		return res
	else:
		return None

def getOrgInfo(orgName):
	""" Lookup Organization Information """
	res = gitHubRequest("https://api.github.com/orgs/{}".format(orgName))
	#pprint(res)
	if res != None:
		print "Organization URL :", res["html_url"]
		print "Organization ID  :", res["id"]
		print "No. Public Repos :", res["public_repos"]
		print "No. Private Repos:", res["owned_private_repos"]

def generateOrgPofile(orgName):
	""" Generate Organization Profile """
	orgRes = gitHubRequest("https://api.github.com/orgs/{}".format(orgName))
	if orgRes != None:
		orgPorfileList = []
		# Org info
		orgPorfileList.append("[github_org]")
		orgPorfileList.append("name = {}".format(orgRes["login"]))
		orgPorfileList.append("id = {}".format(orgRes["id"]))
		orgPorfileList.append("url = {}".format(orgRes["html_url"]))
		orgPorfileList.append("")
		# Team info
		orgPorfileList.append("[org_teams]")
		teamRes = gitHubRequest("https://api.github.com/orgs/{}/teams".format(orgName))
		for t in teamRes:
			orgPorfileList.append("{} = {}".format(t["name"], t["id"]))
		orgPorfileList.append("")
		# Member info
		orgPorfileList.append("[org_members]")
		memberRes = gitHubRequest("https://api.github.com/orgs/{}/members".format(orgName))
		for m in memberRes:
			orgPorfileList.append("{} = {}".format(m["login"], m["id"]))
		
		# Write info to file
		orgProfileFileName = "{}.profile".format(orgName)
		orgProfileFile = open(orgProfileFileName, "w")
		for l in orgPorfileList:
			orgProfileFile.writelines("{}\n".format(l))
		orgProfileFile.close()
		"""print "[INFO][PROFILE GENERATED] in {}".format(orgProfileFileName)
		FIX ME"""

 

def getTeamDetails(teamID):
	""" List Team Members """
	tid = ""
	tname = ""
	tperm = ""
	tmembers = 0
	trepos = 0
	
	if teamID.isdigit() == True:
		tid = teamID
	else:
		print "[ERROR] Need Team ID. {} is not enough information".format(tid)
		return
	
	# get Team Info
	res = gitHubRequest("https://api.github.com/teams/{}".format(tid))
	if res != None:
		tname = res["name"]
		tperm = res["permission"]
		tmembers = res["members_count"]
		trepos = res["repos_count"]
	else:
		print "[ERROR][TEAM {}] No such team.".format(tid)
		return
	
	# get Team Members	
	res = gitHubRequest("https://api.github.com/teams/{}/members".format(tid))
	if res != None:
		#pprint(res)
		if(len(res) >= 1):
			memberList = ""
			for r in res:
				memberList += " " + r["login"]
			print "[INFO][TEAM {}] Name: {}, Permissions: {}, No. Repos: {}, Members[{}]:{}".format(tid, tname, tperm, trepos, tmembers, memberList)
		else:
			print "[INFO][TEAM {}] Name: {}, Permissions: {}, No. Repos: {}, Members[{}]: None".format(tid, tname, tperm, trepos, tmembers)
	else:
		print "[ERROR] No teams exist"

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

def addRepository(orgName, repoName, description, isPrivate, gitignore):
	""" Add a new repository to the organization """
	""" FIX ME: need to use optional parameters and then set defaults """
	payload = {}
	payload["name"] = repoName
	if description != None:
		payload["description"] = description
	payload["private"] = isPrivate
	payload["has_issues"] = True
	payload["has_wiki"] = True
	payload["has_downloads"] = True
	payload["auto_init"] = True
	if gitignore != None:
		payload["gitignore_template"] = gitignore
	
	
	res = gitHubPost("https://api.github.com/orgs/{}/repos".format(orgName), payload)
	if res != None:
		print "[INFO][CREATE REPO] {}/{}".format(orgName, repoName)
	else:
		print "[ERROR][CREATE REPO] Failed to create repo {}/{}".format(orgName, repoName)

def addOrgTeam(orgName, newTeam, teamPermissions):
	""" Add new team to the organization """
	res = gitHubPost("https://api.github.com/orgs/{}/teams".format(orgName), {"name":newTeam, "permission":teamPermissions})
	if res != None:
		print "[INFO][CREATE TEAM] ID = {}, Name = {}".format(res["id"], res["name"])
	else:
		print "[ERROR][CREATE TEAM] Failed to create team {}".format(newTeam)
	
def addOrgMember2Team(orgTeam, orgMember):
	""" Add a GitHub user to an organization-based team """
	res = gitHubPut("https://api.github.com/teams/{}/members/{}".format(orgTeam, orgMember))
	if res == True:
		print "[INFO][ADD MEMBER] {} added to team {}".format(orgMember, orgTeam)
	else:
		print "[ERROR][CREATE MEMBER] Failed to add member {} to team {}".format(orgMember, orgTeam)

def addOrgRepo2Team(orgName, orgTeam, orgRepo):
	""" Add a repository to an organization-based team """
	res = gitHubPut("https://api.github.com/teams/{}/repos/{}/{}".format(orgTeam, orgName, orgRepo))
	if res == True:
		print "[INFO][ADD TEAM] {} added to the {}/{}".format(orgTeam, orgName, orgRepo)
	else:
		print "[ERROR][ADD TEAM] {} added to the {}/{}".format(orgTeam, orgName, orgRepo)

def addWebHook(orgName, repoName, hookURL):
	""" Add a Web Hook to the Repository"""
	payload = {}
	payload["name"] = "web"
	payload["active"] = True
	payload["events"] = [ "push", "pull_request" ]
	payload["config"] = { "url" : hookURL, "content_type": "json"  }
	
	pprint(payload)
	
	res = gitHubPost("https://api.github.com/repos/{}/{}/hooks".format(orgName, repoName), payload)
	
	if res != None:
		print "[INFO][ADD Hook] {} added to the {}/{}".format(res["url"], orgName, repoName)
	else:
		print "[ERROR][ADD Hook] No hook added to {}/{}".format(orgName, repoName)

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
addParser = subParser.add_parser("add", help="Add resources to specified organization")
addParser.add_argument("-p", "--profile", help="use an org profile to perform add operations", nargs=1, dest="addProfile")
addParser.add_argument("-r", "--repo", help="perform operations on repositories", nargs=1, dest="addRepo")
addParser.add_argument("-t", "--team", help="perform operations on teams", nargs=1, dest="addTeam")
addParser.add_argument("-e", "--perm", help="level of permission", choices=["pull", "push", "admin"], dest="addPerm", default="pull")
addParser.add_argument("-m", "--member", help="perform operations on members", nargs=1, dest="addMember")
addParser.add_argument("-k", "--hook", help="perform operations on hooks", nargs=1, dest="addHook")

args = parser.parse_args()
#pprint(args)

"""
    Manage user Requests
"""
# list --profile
if 'listProfile' in args and args.listProfile:
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
elif 'listTeamID' in args and args.listTeamID != None:
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
		for t in args.listTeamID:
			getTeamDetails(t)

# list --member (no teams specified)
elif 'listTeamID' in args and args.listMemberID != None:
	# list --member (all members)
	if len(args.listMemberID) == 0:
		listOrgMembers(args.org)
	else:
		unsupportedFeature("listings involving more than one team member")

# add --team t1
elif 'addTeam' in args and args.addTeam != None and args.addMember == None and args.addRepo == None and args.addHook == None:
	addOrgTeam(args.org, args.addTeam[0], args.addPerm)

# add --member m1
elif 'addTeam' in args and args.addTeam == None and args.addMember != None and args.addRepo == None and args.addHook == None:
	print "[ERROR][ADD MEMBER] GitHub does not allow adding members without teams"
	
# add --team t1 --member m1
elif 'addTeam' in args and args.addTeam != None and args.addMember != None and args.addRepo == None and args.addHook == None:
	orgProfileFile = ""
	if args.addProfile != None:
		orgProfileFile = args.addProfile[0]
	else:
		generateOrgPofile(args.org)
		orgProfileFile = "{}.profile".format(args.org)
	
	orgProfileParser = SafeConfigParser()
	orgProfileParser.read(orgProfileFile)
	
	try:
		teamID = orgProfileParser.get("org_teams", args.addTeam[0])
		addOrgMember2Team(teamID, args.addMember[0])
	except ConfigParser.NoOptionError:
		print "[ERROR][ADD MEMBER] {} team does not exist in {}".format(args.addTeam[0], args.org)

# add --repo r1
elif 'addRepo' in args and args.addTeam == None and args.addMember == None and args.addRepo != None and args.addHook == None:
	""" Using default options for repo - should fix for better usability """
	""" FIX ME: take options from commandline """
	addRepository(args.org, args.addRepo[0], "private lab repository for CS 102 student", True, "C++")

# add --repo r1 --hook url
elif 'addRepo' in args and args.addTeam == None and args.addMember == None and args.addRepo != None and args.addHook != None:
	""" Add web hook to repo """
	addWebHook(args.org, args.addRepo[0], args.addHook[0])

# add --repo r1 --team t1
elif 'addRepo' in args and args.addTeam != None and args.addMember == None and args.addRepo != None and args.addHook == None:
	orgProfileFile = ""
	if args.addProfile != None:
		orgProfileFile = args.addProfile[0]
	else:
		generateOrgPofile(args.org)
		orgProfileFile = "{}.profile".format(args.org)
	
	orgProfileParser = SafeConfigParser()
	orgProfileParser.read(orgProfileFile)
	
	try:
		teamID = orgProfileParser.get("org_teams", args.addTeam[0])
		addOrgRepo2Team(args.org, teamID, args.addRepo[0])
	except ConfigParser.NoOptionError:
		print "[ERROR][ADD MEMBER] {} team does not exist in {}".format(args.addTeam[0], args.org)

# no-option specified
else:
	getOrgInfo(args.org)
""" # """
