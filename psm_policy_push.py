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


from textual.app import App
from textual.widgets import Button, Footer
from textual import events
from textual.views import GridView
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

PSM_IP = 'https://10.9.7.245'
username = 'admin'
password = 'Pensando0$'


#Create auth session

session = pen_auth.psm_login(username, password, PSM_IP)

#if login does not work exit the program
if session is None:
    print ("Login Failed")
    exit()


#Connect to mongodb



# Connect to MongoDB (adjust the connection string as needed)
client = MongoClient('mongodb://localhost:27017/')
db = client['10_9_9_70']  

# Collections
psms_collection = db['policyList']  # Adjust collection names as needed
policies_collection = db['policys']


#pull policies from mongo

#prompt user input on what policies to push


class PSMApp(App):
    async def on_mount(self) -> None:
        # Create a grid layout
        grid = GridView()
        await grid.add_column("main", repeat=1)
        await grid.add_row("row1", size=3)
        await grid.add_row("row2", size=3)
        await grid.add_row("row3", size=3)
        await grid.add_areas(
            select_psm="main,row1",
            select_policy="main,row2",
            push_policy="main,row3"
        )
        self.select_psm_button = Button("Select PSM", id="select_psm")
        self.select_policy_button = Button("Select Policy", id="select_policy")
        self.push_policy_button = Button("Push Policy to PSM", id="push_policy")

        grid.place(
            select_psm=self.select_psm_button,
            select_policy=self.select_policy_button,
            push_policy=self.push_policy_button
        )

        await self.view.dock(grid, edge="top")
        self.footer = Footer()
        await self.view.dock(self.footer, edge="bottom")

    async def handle_button_pressed(self, event: events.ButtonPressed) -> None:
        if event.id == "select_psm":
            message = "Selected PSM: Example PSM"
        elif event.id == "select_policy":
            message = "Selected Policy: Example Policy"
        elif event.id == "push_policy":
            message = "Pushed Policy to PSM: Success"
        else:
            message = "Unknown action"
        
        self.footer.update(message)

    async def on_button_pressed(self, event: events.ButtonPressed) -> None:
        await self.handle_button_pressed(event)

if __name__ == "__main__":
    app = PSMApp()
    app.run()


#comfirm new policies are pushed
