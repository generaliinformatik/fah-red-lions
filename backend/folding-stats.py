
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

import os
import sys
import json
import re
import subprocess
from json import loads, dumps
import sqlite3
import datetime
import requests
from datetime import datetime as dt

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



mypath = os.path.dirname(os.path.realpath(sys.argv[0]))
#print("mypath = ", mypath)

# Load config
config_file = mypath + "/folding-stats.json"
with open(config_file, 'r') as cfg:
    config = loads(cfg.read())

url=getconfig(config,"baseurl","")+str(getconfig(config,"team"))
myResponse = requests.get(url)

# For successful API call, response code will be 200 (OK)
if(myResponse.ok):
    jStats = json.loads(myResponse.content)

    # read rid file (old rank)
    rank_old = 0
    if getconfig(config,"database/rid","") != "":
        try:
            with open(mypath + "/" + getconfig(config,"database/rid",""), 'r') as f:
                rank_old = f.readline()
                f.close()
            #print("Previous rank    : ", str(rank_old))
        except IOError:
            #print("Could not read file:", mypath + "/" + getconfig(config,"database/rid",""))
            pass

    rank_new = getconfig(jStats,"rank","0")
    #print("Current rank: ", rank_new)

    # write rid file (new rank (or old if not updated))
    rank_updated = False
    # rank id file
    if getconfig(config,"database/rid","") != "":
        # write csv if value is given
        with open(mypath + "/" + getconfig(config,"database/rid",""), 'w') as f:
            f.write(str(rank_new))
            f.close()

        if int(rank_new) != int(rank_old):
            rank_updated = True

    # update database/csv if rank was changed
    if rank_updated == True:
        print("Rank changed (%s -> %s / %s)" % (rank_old, rank_new, dt.now()))

        # write database
        conn = sqlite3.connect(mypath + "/" + getconfig(config,"database/sqlite",""))
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS stats(datetime TEXT, team integer, rank integer)')
        cur.execute("INSERT INTO stats VALUES(datetime('now', 'localtime'), 263581, "+str(rank_new)+")")
        conn.commit()
        # Close the connection
        conn.close()

        # write csv
        if getconfig(config,"database/csv","") != "":
            #print("Rank changed. CSV file is being updated...")

            # write csv if value is given
            with open(mypath + "/" + getconfig(config,"database/csv",""), 'w+') as f:
                x = datetime.datetime.now()
                f.write(x.strftime("%Y-%m-%d %X") + ","+str(getconfig(config,"team"))+","+str(rank_new))
                f.close()
    else:
        #print("Rank unchanged.")
        pass

else:
  # If response code is not ok (200), print the resulting http error code with description
    myResponse.raise_for_status()