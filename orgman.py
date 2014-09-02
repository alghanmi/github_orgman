#!/usr/bin/env python

import ConfigParser
from ConfigParser import SafeConfigParser
from pprint import pprint
import csv
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
		if 'next' in r.links:
			res.extend(gitHubRequest(r.links['next']['url']))
        
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
		if "errors" in res:#added by monroe
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
		#pprint(res)
		details = ""
		if "errors" in res:
			for e in res["errors"]:
				details += "{}.{}: {}.".format(e["resource"], e["field"], e["code"])
		print "[ERROR][HTTP {}] {} - {}".format(r.status_code, res["message"], details)
		return False
		
def gitHubPatch(url, payload):
	""" Send a PATCH request to GitHub via API"""
	# http://developer.github.com/v3/orgs/teams/#edit-team
	r = requests.patch(url, data=simplejson.dumps(payload), auth=(githubUsername, githubPassword))
	if r.status_code == 200:
		return True
	else:
		res = simplejson.loads(r.content)
		#pprint(res)
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

def listOrgRepos(orgName):
	""" List All repositories within an org
    FIX ME: add an option to list repo details """
	res = gitHubRequest("https://api.github.com/orgs/{}/repos".format(orgName))
	
	if res != None:		
		repoCount = 0
		for r in res:
			repoCount += 1
			
			print "{}".format(r["ssh_url"])
				
	else:
		print "[INFO] No repositories exist"

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

def addLabel(orgName, repoName, labelName, labelColor):
	""" Add a new label to the issue tracker of a repo """
	payload = {"name":labelName, "color":labelColor}

	res = gitHubPost("https://api.github.com/repos/{}/{}/labels".format(orgName, repoName), payload)
	if res != None:
		print "[INFO][CREATE LABEL] {} colored {} in {}/{}".format(res["name"], res["color"], orgName, repoName)
	else:
		print "[ERROR][CREATE LABEL] Failed to create {} in {}/{}".format(labelName, orgName, repoName)

def addMilestone(orgName, repoName, milestoneTitle, milestoneDesc, milestoneDue):
	""" Add a new Mailestone to the issue tracker of a repo """
	payload = {"title":milestoneTitle}
	if milestoneDue:
		payload["due_on"] = milestoneDue
	if milestoneDesc:
		payload["description"] = milestoneDesc

	res = gitHubPost("https://api.github.com/repos/{}/{}/milestones".format(orgName, repoName), payload)
	if res != None:
		print "[INFO][CREATE MILESTONE] {}.{} due on {} in {}/{}".format(res["number"], res["title"], res["due_on"], orgName, repoName)
		return res["number"]
	else:
		print "[ERROR][CREATE MILESTONE] Failed to create {} in {}/{}".format(milestoneTitle, orgName, repoName)

def addIssue(orgName, repoName, issueTitle, issueBody, issueAssignee, milestone, issueLabel):
	""" Add a new issue to the issue tracker of a repo """
	labels = [ issueLabel ]
	payload = {"title":issueTitle, "body":issueBody, "assignee":issueAssignee, "milestone":milestone, "labels":labels}

	res = gitHubPost("https://api.github.com/repos/{}/{}/issues".format(orgName, repoName), payload)
	if res != None:
		print "[INFO][CREATE ISSUE] {}.{} in {}/{}".format(res["number"], res["title"], orgName, repoName)
		return res["number"]
	else:
		print "[ERROR][CREATE ISSUE] Failed to create {} in {}/{}".format(issueTitle, orgName, repoName)

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
	
	#pprint(payload)
	
	res = gitHubPost("https://api.github.com/repos/{}/{}/hooks".format(orgName, repoName), payload)
	
	if res != None:
		print "[INFO][ADD Hook] {} added to the {}/{}".format(res["url"], orgName, repoName)
	else:
		print "[ERROR][ADD Hook] No hook added to {}/{}".format(orgName, repoName)

def listOrgMembers(orgName):
	""" List Organization Members """
	res = gitHubRequest("https://api.github.com/orgs/{}/members".format(orgName))
	printMembers(res)



def updateTeamNameAndPermissions(teamID, newName, newPerm):
	payload = {"name":newName}
	if newPerm !=None:
		payload["permission"]=newPerm
		
	res = gitHubPatch("https://api.github.com/teams/{}".format(teamID), payload)
	if res == True:
		print "[INFO][UPDATE TEAM] Team #{} changed to name:{}/perm:{}".format(teamID, newName, ("(permission left alone)" if newPerm==None else newPerm))
	else:
		print "[ERROR][UPDATE TEAM] Team #{} couldn't be changed to name:{}/perm:{}".format(teamID, newName, ("(permission left alone)" if newPerm==None else newPerm))








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
listParser.add_argument("-s", "--repos", help="list repos", action="store_true", dest="listRepos")

# Add Commands
addParser = subParser.add_parser("add", help="Add resources to specified organization")
addParser.add_argument("-p", "--profile", help="use an org profile to perform add operations", nargs=1, dest="addProfile")
addParser.add_argument("-r", "--repo", help="perform operations on repositories", nargs=1, dest="addRepo")
addParser.add_argument("-t", "--team", help="perform operations on teams", nargs=1, dest="addTeam")
addParser.add_argument("-e", "--perm", help="level of permission", choices=["pull", "push", "admin"], dest="addPerm", default="pull")
addParser.add_argument("-m", "--member", help="perform operations on members", nargs=1, dest="addMember")
addParser.add_argument("-k", "--hook", help="perform operations on hooks", nargs=1, dest="addHook")
addParser.add_argument("-i", "--issues", help="perform operations on issue tracker using file", nargs=1, dest="addIssue")

# Update Commands
updateParser = subParser.add_parser("update", help="Change a team name or permission level")
updateParser.add_argument("-t", "--team", help="specify team to modify", nargs=1, dest="updateTeam")
updateParser.add_argument("-e", "--perm", help="modify permission level of team", choices=["pull", "push","admin"], dest="updatePerm")
updateParser.add_argument("-n","--name", help="new name for team", dest="updateName", nargs=1)
updateParser.add_argument("-p", "--profile", help="use an existing org profile to perform update operations", nargs=1, dest="updateProfile")

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
	
# list --repos
if 'listRepos' in args and args.listRepos:
	# List all repos in the organization
	if args.listTeamID == None and args.listMemberID == None:
		listOrgRepos(args.org)
	# List all team repos
	elif args.listTeamID != None and args.listMemberID == None:
		unsupportedFeature("List all team repos")
	# List all member repos (within the organization)
	elif args.listTeamID == None and args.listMemberID != None:
		unsupportedFeature("List all member repos (within the organization)")
	# List repos belonging to both a team and a member
	else:
		unsupportedFeature("List repos belonging to both a team and a member")
		

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
elif 'addTeam' in args and args.addTeam != None and args.addMember == None and args.addRepo == None and args.addHook == None and args.addIssue == None:
	addOrgTeam(args.org, args.addTeam[0], args.addPerm)

# add --member m1
elif 'addTeam' in args and args.addTeam == None and args.addMember != None and args.addRepo == None and args.addHook == None and args.addIssue == None:
	print "[ERROR][ADD MEMBER] GitHub does not allow adding members without teams"
	
# add --team t1 --member m1
elif 'addTeam' in args and args.addTeam != None and args.addMember != None and args.addRepo == None and args.addHook == None and args.addIssue == None:
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
elif 'addRepo' in args and args.addTeam == None and args.addMember == None and args.addRepo != None and args.addHook == None and args.addIssue == None:
	""" Using default options for repo - should fix for better usability """
	""" FIX ME: take options from commandline """
	addRepository(args.org, args.addRepo[0], "Private programming assignment repository", True, "C++")

# add --repo r1 --hook url
elif 'addRepo' in args and args.addTeam == None and args.addMember == None and args.addRepo != None and args.addHook != None and args.addIssue == None:
	""" Add web hook to repo """
	addWebHook(args.org, args.addRepo[0], args.addHook[0])

# add --repo r1 --team t1
elif 'addRepo' in args and args.addTeam != None and args.addMember == None and args.addRepo != None and args.addHook == None and args.addIssue == None:
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

# add --repo r1 --issues issue_file --member USER_NAME
elif 'addRepo' in args and args.addTeam == None and args.addMember != None and args.addRepo != None and args.addHook == None and args.addIssue != None:
	""" Add milestones to repo """
	issueParser = SafeConfigParser()
	issueParser.optionxform = str  # override optionxform so ConfigParser becomes case insensitive
	issueParser.read(args.addIssue[0])
	#print issueParser.sections()
	if issueParser.has_section("labels"):
		labels = issueParser.items("labels")
		for l in labels:
			l_name = l[0]
			l_color = l[1]
			addLabel(args.org, args.addRepo[0], l_name, l_color)

	if issueParser.has_section("milestones"):
		milestones = issueParser.items("milestones")
		for m in milestones:
			try:
				m_id = m[0]
				m_name = m[1]
				m_desc = None
				m_date = None
				m_issues = { }
				
				for i in issueParser.items(m[0]):
					i_name = i[0]
					i_data = i[1]
					
					if i_name == "description":
						m_desc = i_data
					elif i_name == "date":
						m_date = i_data
					else:
						#Assuming is issue
						issue = csv.reader(i_data, skipinitialspace=True)
						issue_title = None
						issue_desc = None
						issue_label = None
						delim_count = 0
						for s in issue:
							if s and s[0] and delim_count == 0:
								issue_title = s[0]
							elif s and s[0] and delim_count == 1:
								issue_desc = s[0]
							elif s and s[0] and delim_count == 2:
								issue_label = s[0]
							if s and s[0]:
								delim_count += 1
						m_issues[i_name] = [issue_title, issue_desc, issue_label]
						
				m_gh_id = addMilestone(args.org, args.addRepo[0], m_name, m_desc, m_date)
				for mi in sorted(m_issues.iterkeys()):
					addIssue(args.org, args.addRepo[0], m_issues[mi][0], m_issues[mi][1], args.addMember[0], m_gh_id, m_issues[mi][2])
					#print "{}, {}, {}, {}, {}, {}, {}".format(args.org, args.addRepo[0], m_issues[mi][0], m_issues[mi][1], args.addMember[0], m_gh_id, m_issues[mi][2])
				
			except ConfigParser.NoSectionError:
				print "[ERROR][ADD ISSUES] Invalid section '{}'. Section ignored".format(m[0])
		
	else:
		print "[ERROR][ADD ISSUES] Invalid file format {}, no milestones section"

# update --team t1 [[--name newName] || [--perm newPerm]]
elif 'updateTeam' in args and ( args.updateName != None or args.updatePerm != None):
	orgProfileFile = ""
	if args.updateProfile != None:
		orgProfileFile = args.updateProfile[0]
	else:
		generateOrgPofile(args.org)
		orgProfileFile = "{}.profile".format(args.org)
	
	orgProfileParser = SafeConfigParser()
	orgProfileParser.read(orgProfileFile)
	
	try:
		teamID = orgProfileParser.get("org_teams", args.updateTeam[0])
		updateTeamNameAndPermissions(teamID, (args.updateTeam[0] if args.updateName==None else args.updateName[0]), args.updatePerm)
	except ConfigParser.NoOptionError:
		print "[ERROR][UPDATE TEAM] {} team does not exist in organization {}".format(args.updateTeam[0], args.org)

elif 'updateTeam' in args and args.updateName == None and args.updatePerm == None:
	#no options provided... error
	print "[ERROR][UPDATE TEAM] Must provide a new name or new permission to update team '{}' with.".format(args.updateTeam[0])
	
# no-option specified
else:
	getOrgInfo(args.org)
""" # """
