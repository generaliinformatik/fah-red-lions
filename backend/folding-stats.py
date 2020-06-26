
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (C) 2020 Generali AG, Rene Fuehrer <rene.fuehrer@generali.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import os
import sys
import json
import csv
import re
import subprocess
from json import loads, dumps
import sqlite3
import datetime
import requests
from datetime import datetime as dt
import logging

def initialize_logger(output_dir):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to info
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)-8s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "folding-stats-error.log"),"a", encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)-8s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "folding-stats.log"),"a")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)-8s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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

initialize_logger(mypath+"/logs/")

logging.debug("Script was started at %s", (dt.now()))

# Load config
config_file = mypath + "/folding-stats.json"
with open(config_file, 'r') as cfg:
    config = loads(cfg.read())

logging.info("Checking Folding@Home stats...")
uid_datetime=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
logging.info("UID_DATETIME=%s", (uid_datetime))
url=getconfig(config,"baseurl","")+str(getconfig(config,"team"))
myResponse = requests.get(url)

# For successful API call, response code will be 200 (OK)
if(myResponse.ok):
    jStats = json.loads(myResponse.content)

    # read rid file (old rank)
    rank_old = 0
    rank_new = 0
    if getconfig(config,"database/rid","") != "":
        try:
            with open(mypath + "/" + getconfig(config,"database/rid",""), 'r') as f:
                rank_old = f.readline()
                f.close()
            logging.debug("Previous rank : %s", (str(rank_old)))
        except IOError:
            logging.warning("Could not read file: %s", (mypath + "/" + getconfig(config,"database/rid","")))
            pass

    rank_new = getconfig(jStats,"rank","0")
    logging.debug("Current rank  : %s", (rank_new))

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
        logging.info("Rank changed (%s -> %s)", rank_old, rank_new)

        if getconfig(config,"database/sqlite","") != "":
            # write database
            logging.info("Rank changed. SQlite is being updated...")
            file_db = mypath + "/" + getconfig(config,"database/sqlite","")
            logging.debug("filename: %s", (file_db))
            conn = sqlite3.connect(file_db)
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS stats(datetime TEXT, uid_datetime TEXT, team integer, rank integer, change)')
            cur.execute('CREATE VIEW IF NOT EXISTS view_stats AS SELECT datetime,uid_datetime,team,rank,(LAG ( rank, 1, 0 ) OVER (ORDER BY datetime) - rank ) change FROM stats')
            cur.execute('CREATE VIEW IF NOT EXISTS view_supporter AS SELECT s.uid_datetime,group_concat(t.name, ", ") as supporter FROM stats s, team t WHERE s.uid_datetime = t.uid_datetime AND t.supporter=1 GROUP BY s.uid_datetime')

            # Here we calculate the difference (change) of the rank in relation
            # to the row before as a backup.
            # The main calculation is done by the sqlite view 'view_stats' where
            # the difference is calculated by the LAG() function. Export is done
            # by exporting the view later where the difference is automatically
            # calculated!
            change_indicator = 0
            try:
                cur.execute("select rank from stats ORDER by datetime DESC LIMIT 1")
                record = cur.fetchone()
                rank_old = record[0]
                logging.info("old db rank=%s" % (rank_old))
                change_indicator = rank_old - rank_new
                # new rank lower than the old rank
                if change_indicator > 0:
                    logging.debug("new rank < from db detected")
                # new rank higher than the old rank
                if change_indicator < 0:
                    logging.debug("new rank > from db detected")
            except:
                # rank unchanged or invalid
                change_indicator = 0

            cur.execute("INSERT INTO stats VALUES(datetime('now', 'localtime'), '"+uid_datetime+"',263581, "+str(rank_new)+"," + str(change_indicator) + ")")
            conn.commit()

            # getting team member stats (only if team rank is changed)
            logging.info("Getting team member stats...")
            for member in getconfig(jStats,"donors"):
                member_name=member["name"]
                logging.info("Collecting team meber data of '%s'", str(member_name))
                member_id=member["id"]
                try:
                    member_rank=member["rank"]
                    sql_select_Query = "select credit from (select * from team where id="+str(member_id)+" order by datetime DESC LIMIT 2) ORDER BY datetime ASC LIMIT 1"
                    cur = conn.cursor()
                    cur.execute(sql_select_Query)
                    record = cur.fetchone()

                    member_supporter=0
                    member_credit=member["credit"]
                    member_old_credit=record[0]
                    logging.info("checkin changed credits (old/new credits): %s => %s" % (str(member_old_credit), str(member_credit)))
                    if member_credit != member_old_credit:
                        member_supporter=1
                        logging.info("member IS A SUPPORTER of this rank change")
                    else:
                        member_supporter=0
                        logging.info("member is not a supporter of this rank change")
                except:
                    member_rank=999999
                    member_supporter=0

                member_credit=member["credit"]
                logging.info("%s (%s)", member_name, member_id)

                cur.execute('CREATE TABLE IF NOT EXISTS team(datetime TEXT, uid_datetime TEXT, id INTEGER, name TEXT, rank integer, credit INTEGER, supporter INTEGER)')
                cur.execute("INSERT INTO team VALUES(datetime('now', 'localtime'), '"+uid_datetime+"', "+str(member_id)+", '"+str(member_name)+"', "+str(member_rank)+", "+str(member_credit)+", "+str(member_supporter)+")")

                conn.commit()

#            # Close the connection
#            conn.close()
        else:
            logging.info("No CSV file given.")

        # write csv
        if getconfig(config,"database/csv","") != "":
            logging.info("Rank changed. CSV file is being updated...")

            # write csv if value is given
            file_csv = mypath + "/" + getconfig(config,"database/csv","")

            # initialize csv header if file is not present 
            logging.debug("filename: %s", (file_csv))
            cursor = conn.cursor()
            cursor.execute("select * from view_stats")
            with open(file_csv, "w") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=",")
                csv_writer.writerow([i[0] for i in cursor.description])
                csv_writer.writerows(cursor)
        else:
            logging.info("No CSV file given.")

        # write csv
        if getconfig(config,"database/csv","") != "":
            logging.info("Rank changed. CSV file is being updated...")

            # write csv if value is given
            file_csv = mypath + "/" + getconfig(config,"database/supporter","")

            # initialize csv header if file is not present 
            logging.debug("filename: %s", (file_csv))
            cursor = conn.cursor()
            cursor.execute("select * from view_supporter")
            with open(file_csv, "w") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=",")
                csv_writer.writerow([i[0] for i in cursor.description])
                csv_writer.writerows(cursor)
        else:
            logging.info("No CSV file given.")
    else:
        logging.info("Rank unchanged (%s).", rank_new)
        pass

else:
    # If response code is not ok (200), print the resulting http error code with description
    myResponse.raise_for_status()
