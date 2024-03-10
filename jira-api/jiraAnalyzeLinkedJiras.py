#!/usr/bin/python3
#
# Generates csv containing a summary of all linked 'depends on' Jiras
#
from atlassian import Jira
from datetime import datetime

delimeter = ";"
jiraList = ("CN-83503","CN-76495","CN-76496")
fileName = "/media/sf_shared/"+datetime.now().strftime("%m%d%Y-%H%M%S")+".csv"
tokenID = "NDYwMzcwNjc3NzM1OqcurZVnUPZPRPUMAXBxfaRsJnoQ"

jira = Jira(url="https://jira.adtran.com", token=tokenID)
file = open(fileName,"w")
try:
    for jiraID in jiraList:
        foundOne = False
        parentIssue = jira.issue (jiraID)
        for linkedIssue in parentIssue["fields"]["issuelinks"]:
            if (("outwardIssue" in linkedIssue) & (linkedIssue["type"]["name"] == "Depends")):
                try:
                    newIssue = jira.issue(linkedIssue["outwardIssue"]["key"])
                    file.write (parentIssue["key"]+delimeter+newIssue["key"]+delimeter+newIssue["fields"]["status"]["name"]+delimeter+newIssue["fields"]["summary"]+"\n")
                    foundOne = True
                except: print (parentIssue["key"]+" - Failed to retrieve linked Jira information for "+linkedIssue["outwardIssue"]["key"])
        if not foundOne: print (parentIssue["key"]+" - Does not contain linked 'depends on' Jiras")
except: print (parentIssue["key"]+" - Failed to retreive list of linked Jiras")
file.close()