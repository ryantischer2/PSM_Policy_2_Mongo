# Copyright (c) 2024, AMD
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# Author: Ryan Tischer ryan.tischer@amd.com

import pen, pen_auth
from pymongo import MongoClient


"""
The following is used for secure password storage.  Uncomment to use.

keyring should work on modern OS.  Only tested on MAC.  Visit the following to make it work in your OS
https://pypi.org/project/keyring/

Must run init program first.
"""

'''
import keyring

creds =  (keyring.get_credential("pensando", "admin"))

with open('pypen_init_data.json') as json_file:
    jdata = json.load(json_file)
    PSM_IP = jdata["ip"]
    username = creds.username
    password = creds.password
#end secure environment vars

#static PSM vars.  Uncomment to use

#input PSM Creds
'''

PSM_IP = 'https://10.9.9.70'
username = 'admin'
password = 'Pensando0$'


#Create auth session

session = pen_auth.psm_login(username, password, PSM_IP)

#if login does not work exit the program
if session is None:
    print ("Login Failed")
    exit()

#pass session to get data
NSP = pen.get_networksecuritypolicy(PSM_IP, session)
numPolicy = len(NSP['items'])
#save policy to mongo

#mongo clients timeout
server_selection_timeout = 5000  # 5 seconds for server selection timeout
connect_timeout = 3000  # 3 seconds for connection timeout
socket_timeout = 5000  # 5 seconds for socket timeout (read/write operations)

# Initialize MongoClient with timeouts
# Connect to MongoDB - Replace 'localhost' and '27017' with your MongoDB host and port if different

try:
    client = MongoClient(
    'localhost', 27017,
    serverSelectionTimeoutMS=server_selection_timeout,
    connectTimeoutMS=connect_timeout,
    socketTimeoutMS=socket_timeout
    )
    pass
except Exception as e:
    print(f"MongoDB connection failed: {e}")


#Create the database 
db = client['AMD'] 
#need to remove the . from the psm url

#create collection for policy overview
collection = db['policyList']
#make index unique and avoid dup records
collection.create_index([('uuid', 1), ('last change time', 1)], unique=True)

#parse psm data for policy details
for i in range(numPolicy):
    data = {
            'name': NSP['items'][i]['meta']['display-name'],
            'uuid': NSP['items'][i]['meta']['name'],  
            'generation': NSP['items'][i]['meta']['generation-id'],  
            'last change time': NSP['items'][i]['meta']['mod-time'],
            'rule count': len(NSP['items'][i]['spec']['rules']),  
            'status': NSP['items'][i]['status']['propagation-status']['status'],
            'psm' : PSM_IP
    }

    try:
        collection.insert_one(data)
        print("Document inserted successfully.")
    except Exception:
        pass
    
#create collection for the policies 
collection = db['policys']
#make index unique and avoid dup records
collection.create_index([('meta.name', 1),('meta.mod-time', 1)], unique=True)  

for i in range(numPolicy):

    #get UUID of policy
    workingPolicyUUID = (NSP['items'][i]['meta']['name'])
    
    #get the specific policy
    workingPolicy = pen.get_Specificpolicy(PSM_IP, session, workingPolicyUUID)
               
    #write to mongo
 
    try:
        collection.insert_one(workingPolicy)
        print("Document inserted successfully.")
    except Exception:
        pass

