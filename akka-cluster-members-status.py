import requests
import json
import socket
import urllib.parse
hostname = socket.gethostname()

from prettytable import PrettyTable

#Provide the Akka Cluster Rest API URL
url = 'http://'+hostname+':25610/cluster/members'

#Make a GET request to the URL
response = requests.get(url)

#Check the response code
if response.status_code == 200:
    #Parse the response into JSON
    data = json.loads(response.content)
    #Create a PrettyTable object
    table = PrettyTable()
    #Add headers to the table
    table.field_names = ["Address", "Roles", "Status"]
    #Iterate over the response data and add it to the table
    for member in data['members']:
        table.add_row([urllib.parse.urlparse(member['node']).hostname, member['roles'][0], member['status']])
    #Print the table
    print(table)
else:
    print("Error: Could not connect to the Akka Cluster Rest API")



result = urllib.parse.urlparse(url)

hostname = result.hostname
