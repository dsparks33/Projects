#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup

#URL to each of the soak jobs
soakJobs = [
    'https://jenkins-m3-hsv.adtran.com/view/Pioneer%20Production%20Pipelines/job/pioneer/job/sdx-aggregation-arm-8205-54/job/main/29/artifact/',
    'https://jenkins-m3-hsv.adtran.com/view/Pioneer%20Production%20Pipelines/job/pioneer/job/sdx-aggregation-arm-8210-54/job/main/32/artifact/',
    'https://jenkins-m3-hsv.adtran.com/view/Pioneer%20Production%20Pipelines/job/pioneer/job/sdx-aggregation-arm-8120-14/job/main/42/artifact/',
    'https://jenkins-m3-hsv.adtran.com/view/Pioneer%20Production%20Pipelines/job/pioneer/job/sdx-aggregation-arm-8205-54M/job/main/32/artifact/',
    'https://jenkins-m3-hsv.adtran.com/view/Pioneer%20Production%20Pipelines/job/pioneer/job/sdx-aggregation-arm-8305-20/job/main/29/artifact/',
    'https://jenkins-m3-hsv.adtran.com/view/Pioneer%20Production%20Pipelines/job/pioneer/job/sdx-aggregation-arm-8310-32/job/main/29/artifact/',
    'https://jenkins-m3-hsv.adtran.com/view/Pioneer%20Production%20Pipelines/job/pioneer/job/sdx-aggregation-arm-8310-64/job/main/30/artifact/'
]

# Process the results for after the completion of a new iteration
def processNewResults(baseURL, iteration):
    print('    '+iteration)
    failureSummary = requests.get(baseURL+iteration+'/failure_summary.txt')
    if failureSummary:
        failureSummaryList = failureSummary.text.split('\n')
        for outputLine in failureSummaryList:
            if 'features passed' not in outputLine:
                if 'steps passed' not in outputLine:
                    if 'Took ' not in outputLine:
                        if 'scenarios passed' in outputLine:
                            outputLine = outputLine[:outputLine.find('failed,')+len('failed,')-1]
                        print('        '+outputLine)
    else: print('        Failed to retrieve the failure_summary.txt file')
    return

# Process all completed iterations for the current job
def processSoakResults(soakURL):
    response = requests.get(soakURL)
    if response:
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                if 'acceptance_results_' in href:
                    processNewResults (soakURL, href)
    else: print('    Failed to read artifacts summary page')
    return

for job in soakJobs:
    print('==================================================================================')
    print('+ '+job.split('arm-')[1].split('/job')[0]+' soak test results:')
    print('+ '+job)
    print('==================================================================================')
    processSoakResults(job)
