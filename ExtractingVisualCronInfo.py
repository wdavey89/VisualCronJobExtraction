import json, pypyodbc, ctypes, requests
from requests import request
from requests.models import Response
import datetime

def main():
    ctypes.windll.kernel32.SetConsoleTitleW('Extracting VisualCron Information')
    print("VisualCron Data Retrieval starting...")
    # Catch statement to ensure appsettings.json file exists, and handle the error if it doesn't.
    try:
        with open('appsettings.json') as appsettings:
            appsettingsData = json.load(appsettings)
            connectionString = appsettingsData['Connection String']
            username = appsettingsData['WebApiUsername']
            password = appsettingsData['WebApiPassword']
            timeout = appsettingsData['WebApiTimeout']              
        conn = getConnectionString(connectionString)
        machines = getMachineNames(conn)
        for machineName in machines:
            apiUrl = "http://{}:8001/VisualCron/json/logon?username={}&password={}&expire={}".format(machineName, username, password, timeout)
            authToken = connectAPI(machineName, apiUrl)
            if authToken == None:
                machines.remove(machineName)
        for machineName in machines:
            apiUrl = "http://{}:8001/VisualCron/json/logon?username={}&password={}&expire={}".format(machineName, username, password, timeout)
            authToken = connectAPI(machineName, apiUrl)
            print("Token Acquired: {} on Server Name: {}".format(authToken, machineName))
            print("[{}] Token Acquired: {} on Server Name: {}".format(datetime.datetime.now().strftime("%H:%M:%S"),authToken, machineName))
            getJobInfo(machineName, authToken, conn)
    except FileNotFoundError:
        print("No appsettings.json file can be found.")
        print("[{}] No appsettings.json file can be found.".format(datetime.datetime.now().strftime("%H:%M:%S")))
        quit()
    conn.close()
    
def getConnectionString(connectionString):
    try:
        conn = pypyodbc.connect(connectionString)
        print("Connected to SQL Server...")
        print("[{}] Connected to SQL Server...".format(datetime.datetime.now().strftime("%H:%M:%S")))
        return conn
    except pypyodbc.Error:
        print("Failed to connect to SQL Server")
        print("[{}] Failed to connect to SQL Server".format(datetime.datetime.now().strftime("%H:%M:%S")))
        quit()

def getMachineNames(conn):
    machines = []
    cursor = conn.cursor()
    cursor.execute("{CALL visualcron.GetMachineNames}")
    rows = cursor.fetchall()
    if len(rows) > 0:
        for row in rows:
            computer = str(row)
            line_out = computer.partition('\'')[-1].rstrip('\',)')
            machines.append(line_out)        
    return machines

def connectAPI(machineName, apiUrl):
    try:
        apiResponse = requests.get(apiUrl)
        jsonResponse = {}
        jsonResponse = apiResponse.json()
        authToken = jsonResponse['Token']
        return authToken
    except requests.ConnectionError:
        print("Unable to connect to URL, please check this is a valid URL, or ensure the WebAPI option is enabled in VisualCron on target machine {}\n".format(machineName))  
        print("[{}] Unable to connect to URL, please check this is a valid URL, or ensure the WebAPI option is enabled in VisualCron on target machine {}\n".format(datetime.datetime.now().strftime("%H:%M:%S"), machineName))
    
def getJobInfo(machineName, authToken, conn):
    connectUrl = "http://{}:8001/VisualCron/json/Job/List?token={}".format(machineName, authToken)
    jobListResponse = requests.get(connectUrl)
    jsonResult = []
    jsonResult = jobListResponse.json()
    listLength = len(jsonResult)
    print("Machine Name: {}".format(machineName))
    print("[{}] Machine Name: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), machineName))
    cursor = conn.cursor()
    i = 0
    while i < listLength:
        try:
            jobName = jsonResult[i]['Name']
            jobDesc = jsonResult[i]['Description']
            groupName = jsonResult[i]['Group']
            jobId = jsonResult[i]['Id']
            jobStatus = jsonResult[i]['Stats']['Active']
            if jobStatus == True:
                jobStatus = 1
            else:
                jobStatus = 0
            lastExecution = jsonResult[i]['Stats']['DateLastExecution']
            numberOfExecutes = jsonResult[i]['Stats']['NoExecutes']
            dateLastExecution = lastExecution.replace('+00:00', '')
            tempDateLastExecution = dateLastExecution.replace('T', ' ')
            dateLastExecution = tempDateLastExecution
            print("Job Name: {}".format(jobName))
            print("Job Description: {}".format(jobDesc))
            print("Group Name: {}".format(groupName))
            print("Job Id: {}".format(jobId))
            print("Job Status: {}".format(jobStatus))
            print("Last Execution: {}".format(lastExecution))
            print("Number of Executes: {}".format(numberOfExecutes))
            print("Date of Last Execution: {}".format(dateLastExecution))
            print("[{}] Job Name: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), jobName))
            print("[{}] Job Description: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), jobDesc))
            print("[{}] Group Name: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), groupName))
            print("[{}] Job Id: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), jobId))
            print("[{}] Job Status: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), jobStatus))
            print("[{}] Last Execution: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), lastExecution))
            print("[{}] Number of Executes: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), numberOfExecutes))
            print("[{}] Date of Last Execution: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), dateLastExecution))
        except TypeError:
            print("Json Result list is likely empty, hence cannot iterate through an empty list")
            print("[{}] Json Result list is likely empty, hence cannot iterate through an empty list".format(datetime.datetime.now().strftime("%H:%M:%S")))
        if len(jobName) > 0:
            try:
                paramaters = (machineName, jobId, jobName, jobDesc or None, groupName, jobStatus, dateLastExecution, numberOfExecutes)
                cursor.execute("{CALL visualcron.AddVisualCronInfo (?,?,?,?,?,?,?,?)}", paramaters)
                print("Executing Stored Procedure: visualcron.AddVisualCronInfo \n")
                print("[{}] Executing Stored Procedure: visualcron.AddVisualCronInfo \n".format(datetime.datetime.now().strftime("%H:%M:%S")))
                conn.commit()
            except NameError:
                print("Cannot execute Stored Procedure")
                print("[{}] Cannot execute Stored Procedure".format(datetime.datetime.now().strftime("%H:%M:%S")))
        else:
            print("Job name is blank, no data to insert")
            print("[{}] Job name is blank, no data to insert".format(datetime.datetime.now().strftime("%H:%M:%S")))
        i += 1
   
if __name__ == "__main__":
    main()