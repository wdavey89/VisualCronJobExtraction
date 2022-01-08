import requests
from requests.api import request
from requests.models import Response

def main():
    machineName = "WAYNE-PC"
    api_url = "http://localhost:8001/VisualCron/json/logon?username=Wayne&password=qiagen09&expire=360000"
    response = requests.get(api_url)
    dict = {}
    dict = response.json()
    authToken = dict["Token"]
    getJobInfo(authToken)
    
    


def getJobInfo(authToken):
    connect_url = "http://localhost:8001/VisualCron/json/Job/List?token={}".format(authToken)
    response2 = requests.get(connect_url)
    result = []
    result = response2.json()
    JobName = result[0]['Name']
    JobDescription = result[0]['Description']
    print(JobName + " - " + JobDescription)
   


if __name__ == "__main__":
    main()
