#!/usr/bin/python3
#
# Simple utility to update a set of Jira filters by replacing one
# character string 'oldString' with another 'newString'.  The set
# of filters modified will be any filter containing 'filterNameMatch'
# within the name.
#
# The user will be prompted to enter a Jira Personal Access Token
# which will be used for authentication.
#
# Note, the filters analyzed have to be marked as a 'favorite' by
# the authenticated user (limitation of the Atlassian Jira library)
#
from atlassian import Jira
import argparse
import getpass

parser = argparse.ArgumentParser()
parser.add_argument ("filterNameMatch", help="The string to identify the filter to update")
parser.add_argument ("oldString", help="The original string to search for and replace in the jql")
parser.add_argument ("newString", help="The new string to replace into the jql")
args = parser.parse_args()
tokenID = getpass.getpass (prompt="Enter your Jira 'Personal Access Token' for authentication: ")

jira = Jira(url="https://jira.adtran.com", token=tokenID)
try:
    filterList = jira.get_filter("favourite")
    print ("Checking "+str(len(filterList))+" filters to match the name '"+args.filterNameMatch+"'...")
    for filter in filterList:
        if args.filterNameMatch in filter["name"]:
            if args.oldString in filter["jql"] :
                newJql = filter["jql"].replace(args.oldString,args.newString)
                try:
                    jira.update_filter(filter["id"], newJql)
                    print("   "+filter["name"]+": updating with '"+args.newString+"'")
                except Exception as e: print ("   "+filter["name"]+": failed to update Jira jql", e)
            else: print ("   "+filter["name"]+": no jql string match for '"+args.oldString+"'")
except: print ("Failed to retreive filter list")
