###############################################################
# Author: Shashank Shekhar.									  #
# Description: generates team vs peer reviewers csv file in   #
# 			   the source directory.						  #
# Prerequisutes: A 'meta' file that should have 			  #
# 				'student,teamname' multiline entries.		  #
###############################################################

import re
import random
import csv
import math
import os

TEAM_PATTERN = r'(.+),(.+)'
META_FILENAME = 'meta'
PR_LIST_FILENAME = 'teams_and_reviewers.csv'
CSV_HEADER = ['TEAM', 'REVIEWER']
MEMBERS = []
TEAMS = set()
MEMBERS_TO_ALLOCATE = None
PR_LIST = []


def readMetaData():
	global TEAMS
	file = open(META_FILENAME, 'r')
	for line in file:
		line = line.strip()
		if not line:
			continue
		match = re.search(TEAM_PATTERN, line)
		if not match:
			continue
		MEMBERS.append({'name': match.group(1), 'team': match.group(2)})
		TEAMS.add(match.group(2))
	TEAMS = list(TEAMS)
		
def shuffle():
	random.shuffle(MEMBERS)
	random.shuffle(TEAMS)
	
def computeAllocation():
	global MEMBERS_TO_ALLOCATE
	totalTeams = len(TEAMS)
	totalMembers = len(MEMBERS)
	MEMBERS_TO_ALLOCATE = int(totalMembers / totalTeams)
	
def matchMembersAgainstTeam():
	# pick one team at a time.
	for oneTeam in TEAMS:
		# pick 'MEMBERS_TO_ALLOCATE' members such that they dont belong to the team that was picked
		# above.
		membersToAllocate = []
		while len(membersToAllocate) != MEMBERS_TO_ALLOCATE:
			member = MEMBERS.pop(0)
			if member['team'] == oneTeam:
				MEMBERS.append(member)
			else:
				membersToAllocate.append(member['name'])
		PR_LIST.append({'team': oneTeam, 'members': membersToAllocate})

	# manage leftover member if any.
	lenTeam = len(TEAMS) - 1
	while MEMBERS:
		member = MEMBERS.pop()
		randomTeam = None
		while True:
			# pick random team from PR_LIST and push left over members into it.
			randomIndex = random.randint(0, lenTeam)
			randomTeam = PR_LIST.pop(randomIndex)
			# do not push if the team already has more than MEMBERS_TO_ALLOCATE peer reviewers or
			# if the peer reviewer is in same team.
			if len(randomTeam['members']) <= MEMBERS_TO_ALLOCATE and member['team'] != randomTeam['team']:
				break
			else:
				PR_LIST.insert(randomIndex, randomTeam)
		randomTeam['members'].append(member['name'])
		PR_LIST.append(randomTeam)

def writeToCsv():
	file = csv.writer(open(PR_LIST_FILENAME, 'w'), lineterminator='\n')
	file.writerow(CSV_HEADER)
	for pr in PR_LIST:
		firstRowOfTeam = False
		for member in pr['members']:
			if not firstRowOfTeam:
				file.writerow([pr['team'], member])
				firstRowOfTeam = True
			else:
				file.writerow([None, member])
		file.writerow([])

# call all methods here.	
readMetaData()
computeAllocation()
shuffle()
matchMembersAgainstTeam()
writeToCsv()

print(PR_LIST_FILENAME + ' ' + 'created in ' + os.getcwd())