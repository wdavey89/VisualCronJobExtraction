import os
import requests
from requests import request
from requests.models import Response


def main():
    machineName = os.environ['COMPUTERNAME']
    connectAPI(machineName)

def connectAPI(machineName):
    apiUrl = "http://localhost:8001/VisualCron/json/logon?username=wayne&password=wayne&expire=360000"
    apiResponse = requests.get(apiUrl)
    jsonResponse = {}
    jsonResponse = apiResponse.json()
    authToken = jsonResponse['Token']
    print("Token Acquired: {}\n".format(authToken))
    getJobInfo(machineName, authToken)
    
def getJobInfo(machineName, authToken):
    connectUrl = "http://localhost:8001/VisualCron/json/Job/List?token={}".format(authToken)
    jobListResponse = requests.get(connectUrl)
    jsonResult = []
    jsonResult = jobListResponse.json()
    listLength = len(jsonResult)
    print("Machine Name: {}".format(machineName))
    i = 0
    while i < listLength:
        jobName = jsonResult[i]['Name']
        jobDesc = jsonResult[i]['Description']
        groupName = jsonResult[i]['Group']
        jobId = jsonResult[i]['Id']
        print("Job Name: {}".format(jobName))
        print("Job Description: {}".format(jobDesc))
        print("Group Name: {}".format(groupName))
        print("Job Id: {}\n".format(jobId))
        i += 1
    
if __name__ == "__main__":
    main()