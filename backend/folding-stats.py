
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Generali AG, Rene Fuehrer <rene.fuehrer@generali.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import json
import re
import subprocess
from json import loads, dumps
import sqlite3
import datetime
import requests

class DictQuery(dict):
    '''
    Dictionary class to get JSON hierarchical data structures

    Parameters:
        dict (dict): Dictionary with hierachical structures

    Returns:
        val (dict): Dictionary where hierachical structured keys be seperated with slashes
    '''
    def get(self, path, default=None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break

        return val

def getconfig(this_dict, this_setting, this_default=""):
    return DictQuery(this_dict).get(this_setting, this_default)



# Load config
config_file = "folding-stats.json"
with open(config_file, 'r') as cfg:
    config = loads(cfg.read())

url=getconfig(config,"baseurl","")+str(getconfig(config,"team"))
# It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
myResponse = requests.get(url)
#print (myResponse.status_code)

# For successful API call, response code will be 200 (OK)
if(myResponse.ok):

    # Loading the response data into a dict variable
    # json.loads takes in only binary or string variables so using content to fetch binary content
    # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
    jStats = json.loads(myResponse.content)

#    print("The response contains {0} properties".format(len(jStats)))
#    print("\n")
#    for key in jStats:
#        print(str(key) + " : " + str(jStats[key]))

    print("Aktueller Rang: ", getconfig(jStats,"rank","0"))

    # Create a database connection
    # (This will create a SQLite3 database called 'tutorial.db'.)
    conn = sqlite3.connect(getconfig(config,"database/sqlite",""))
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS stats(datetime TEXT, team integer, rank integer)')
    cur.execute("INSERT INTO stats VALUES(datetime('now', 'localtime'), 263581, "+str(getconfig(jStats,"rank","0"))+")")
    conn.commit()
    # Close the connection
    conn.close()

    if getconfig(config,"database/csv","") != "":
        # write csv if value is given
        with open(getconfig(config,"database/csv",""), 'w') as f:
            x = datetime.datetime.now()
            f.write(x.strftime("%Y-%m-%d %X") + ","+str(getconfig(config,"team"))+","+str(getconfig(jStats,"rank","0")))
            f.close()

else:
  # If response code is not ok (200), print the resulting http error code with description
    myResponse.raise_for_status()