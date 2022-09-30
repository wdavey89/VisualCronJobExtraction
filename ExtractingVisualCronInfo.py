import os, json, pypyodbc, ctypes, requests
from platform import machine
from requests import request
from requests.models import Response


def main():
    ctypes.windll.kernel32.SetConsoleTitleW('Extracting VisualCron Information')
    machineName = os.environ['COMPUTERNAME']
    with open('appsettings.json') as appsettings:
        appsettingsData = json.load(appsettings)
        connectionString = appsettingsData['Connection String']
        username = appsettingsData['WebApiUsername']
        password = appsettingsData['WebApiPassword']
        timeout = appsettingsData['WebApiTimeout']
        apiUrl = "http://{}:8001/VisualCron/json/logon?username={}&password={}&expire={}".format(machineName, username, password, timeout)             
        conn = getConnectionString(connectionString)
        authToken = connectAPI(machineName, apiUrl)
        print("Token Acquired: {} on Server Name: {}\n".format(authToken, machineName))
        getJobInfo(machineName, authToken, conn)
        conn.close()

def getConnectionString(connectionString):
    try:
        conn = pypyodbc.connect(connectionString)
        print("Connected to SQL Server")
        return conn
    except pypyodbc.Error:
        print("Failed to connect to SQL Server")
        quit()

def connectAPI(machineName, apiUrl):
    try:
        apiResponse = requests.get(apiUrl)
        jsonResponse = {}
        jsonResponse = apiResponse.json()
        authToken = jsonResponse['Token']
        return authToken
    except requests.ConnectionError:
        print("Unable to connect to URL, please check this is a valid URL, or ensure the WebAPI option is enabled in VisualCron on target machine {}".format(machineName))
        quit()  
    
def getJobInfo(machineName, authToken, conn):
    connectUrl = "http://localhost:8001/VisualCron/json/Job/List?token={}".format(authToken)
    jobListResponse = requests.get(connectUrl)
    jsonResult = []
    jsonResult = jobListResponse.json()
    listLength = len(jsonResult)
    print("Machine Name: {}".format(machineName))
    cursor = conn.cursor()
    i = 0
    while i < listLength:
        jobName = jsonResult[i]['Name']
        jobDesc = jsonResult[i]['Description']
        groupName = jsonResult[i]['Group']
        jobId = jsonResult[i]['Id']
        print("Job Name: {}".format(jobName))
        print("Job Description: {}".format(jobDesc))
        print("Group Name: {}".format(groupName))
        print("Job Id: {}".format(jobId))
        try:
            paramaters = (machineName, jobId, jobName, jobDesc, groupName)
            cursor.execute("{CALL visualcron.AddVisualCronInfo (?,?,?,?,?)}", paramaters)
            print("Executing Stored Procedure: visualcron.AddVisualCronInfo \n")
            conn.commit()
        except NameError:
            print("Cannot execute Stored Procedure")
        i += 1
        
   
if __name__ == "__main__":
    main()