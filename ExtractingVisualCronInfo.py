import json, pypyodbc, ctypes, requests
from requests import request
from requests.models import Response

def main():
    ctypes.windll.kernel32.SetConsoleTitleW('Extracting VisualCron Information')
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

def getMachineNames(conn):
    machines = []
    cursor = conn.cursor()
    cursor.execute("{CALL visualcron.GetComputerNames}")
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
        print("Unable to connect to URL, please check this is a valid URL, or ensure the WebAPI option is enabled in VisualCron on target machine {}".format(machineName))
        quit()  
    
def getJobInfo(machineName, authToken, conn):
    connectUrl = "http://{}:8001/VisualCron/json/Job/List?token={}".format(machineName, authToken)
    jobListResponse = requests.get(connectUrl)
    jsonResult = []
    jsonResult = jobListResponse.json()
    listLength = len(jsonResult)
    print("Machine Name: {}".format(machineName))
    cursor = conn.cursor()
    i = 0
    while i < listLength:
        try:
            jobName = jsonResult[i]['Name']
            jobDesc = jsonResult[i]['Description']
            groupName = jsonResult[i]['Group']
            jobId = jsonResult[i]['Id']
            print("Job Name: {}".format(jobName))
            print("Job Description: {}".format(jobDesc))
            print("Group Name: {}".format(groupName))
            print("Job Id: {}".format(jobId))
        except TypeError:
            print("Json Result list is likely empty, hence cannot iterate through an empty list")
        if len(jobName) > 0:
            try:
                paramaters = (machineName, jobId, jobName, jobDesc, groupName)
                cursor.execute("{CALL visualcron.AddVisualCronInfo (?,?,?,?,?)}", paramaters)
                print("Executing Stored Procedure: visualcron.AddVisualCronInfo \n")
                conn.commit()
            except NameError:
                print("Cannot execute Stored Procedure")
        else:
            print("Job name is blank, no data to insert")
        i += 1
      
if __name__ == "__main__":
    main()