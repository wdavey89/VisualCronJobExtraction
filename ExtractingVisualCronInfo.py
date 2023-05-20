import json, pypyodbc, ctypes, requests
from requests import request
from requests.models import Response
import datetime

# Main method. Read in the appsettings.json values for Connection String, username, password and timeout.
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
            print("[{}] Token Acquired: {} on Server Name: {}".format(datetime.datetime.now().strftime("%H:%M:%S"),authToken, machineName))
            getJobInfo(machineName, authToken, conn)
    except FileNotFoundError:
        print("[{}] No appsettings.json file can be found.".format(datetime.datetime.now().strftime("%H:%M:%S")))
        quit()
    conn.close()
    

# Check the connection string to ensure it connects without issue, if it fails, exit the program.
def getConnectionString(connectionString):
    try:
        conn = pypyodbc.connect(connectionString)
        print("[{}] Connected to SQL Server...".format(datetime.datetime.now().strftime("%H:%M:%S")))
        return conn
    except pypyodbc.Error:
        print("[{}] Failed to connect to SQL Server".format(datetime.datetime.now().strftime("%H:%M:%S")))
        quit()

# Retrieve the list of Machine Names from the table 'visualcron.MachineNames'. Then remove the ' from either side of the machine name from the returned result.
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

# Connect to the WebAPI for each machine, to ensure that the API is enabled and can be accessed in order to retrieve a token.
def connectAPI(machineName, apiUrl):
    try:
        apiResponse = requests.get(apiUrl)
        jsonResponse = {}
        jsonResponse = apiResponse.json()
        authToken = jsonResponse['Token']
        return authToken
    except requests.ConnectionError:
        print("[{}] Unable to connect to URL, please check this is a valid URL, or ensure the WebAPI option is enabled in VisualCron on target machine {}\n".format(datetime.datetime.now().strftime("%H:%M:%S"), machineName))
    

# Retrieve the job information for the specific fields from the WebAPI of each machine, and call the Stored Procedure to insert into the database table 'visualcron.VisualCronData'
def getJobInfo(machineName, authToken, conn):
    connectUrl = "http://{}:8001/VisualCron/json/Job/List?token={}".format(machineName, authToken)
    jobListResponse = requests.get(connectUrl)
    jsonResult = []
    jsonResult = jobListResponse.json()
    listLength = len(jsonResult)
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
            print("[{}] Job Name: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), jobName))
            print("[{}] Job Description: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), jobDesc))
            print("[{}] Group Name: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), groupName))
            print("[{}] Job Id: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), jobId))
            print("[{}] Job Status: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), jobStatus))
            print("[{}] Last Execution: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), lastExecution))
            print("[{}] Number of Executes: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), numberOfExecutes))
            print("[{}] Date of Last Execution: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), dateLastExecution))
        except TypeError:
            print("[{}] Json Result list is likely empty, hence cannot iterate through an empty list".format(datetime.datetime.now().strftime("%H:%M:%S")))
        if len(jobName) > 0:
            try:
                paramaters = (machineName, jobId, jobName, jobDesc or None, groupName, jobStatus, dateLastExecution, numberOfExecutes)
                cursor.execute("{CALL visualcron.AddVisualCronInfo (?,?,?,?,?,?,?,?)}", paramaters)
                print("[{}] Executing Stored Procedure: visualcron.AddVisualCronInfo \n".format(datetime.datetime.now().strftime("%H:%M:%S")))
                conn.commit()
            except NameError:
                print("[{}] Cannot execute Stored Procedure".format(datetime.datetime.now().strftime("%H:%M:%S")))
        else:
            print("[{}] Job name is blank, no data to insert".format(datetime.datetime.now().strftime("%H:%M:%S")))
        i += 1
   
if __name__ == "__main__":
    main()