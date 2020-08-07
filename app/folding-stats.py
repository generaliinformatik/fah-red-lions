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
from json import loads
import sqlite3
import datetime
import requests
from datetime import datetime as dt
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from pathlib import Path


def initialize_logger(output_dir):
    """Initialize logging facility

    Args:
        output_dir (str): path to save log file
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to info
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.FileHandler(
        os.path.join(output_dir, "folding-stats-error.log"),
        "a",
        encoding=None,
        delay="true",
    )
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(
        os.path.join(output_dir, "folding-stats.log"), "a"
    )
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class DictQuery(dict):
    """
    Dictionary class to get JSON hierarchical data structures

    Args:
        dict (dict): Dictionary with hierachical structures

    Returns:
        val (dict): Dictionary where hierachical structured keys be seperated with slashes
    """

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
    """Shortcut function to read  config value of given key from
    given dictionary

    Args:
        this_dict (dict): dictionary with key:value
        this_setting (str): key to be read
        this_default (str, optional): defaul if key can not be read. Defaults to "".

    Returns:
        str: read value
    """
    return DictQuery(this_dict).get(this_setting, this_default)


def send_notification(email_subject, email_message):
    try:
        for email_to in email_to_list:
            msg = MIMEMultipart()
            # setup the parameters of the message

            msg["From"] = email_from
            msg["To"] = email_to
            msg["Subject"] = email_subject
            # add in the message body
            msg.attach(MIMEText(email_message, "plain", "utf-8"))
            # create server
            server = smtplib.SMTP(email_server, email_port)
            server.ehlo()
            server.starttls()
            server.ehlo
            # Login Credentials for sending the mail
            server.login(msg["From"], email_password)
            # send the message via the server.

            server.sendmail(msg["From"], msg["To"], msg.as_string())
            server.quit()
            logging.info("Push rank notifcation to: %s", msg["To"])
    except Exception:
        logging.error("Failed to send email notification.")


if __name__ == "__main__":
    mypath = os.path.dirname(os.path.realpath(sys.argv[0]))

    try:
        # create dirs
        Path(mypath + "/data").mkdir(parents=True, exist_ok=True)
        Path(mypath + "/logs").mkdir(parents=True, exist_ok=True)
    except Exception:
        print("Failed to create dirs. Abort.")
        sys.exit(1)

    initialize_logger(mypath + "/logs/")

    logging.debug("Script was started at %s", (dt.now()))
    logging.debug("Script path: %s", (mypath))

    # Load config
    config_file = mypath + "/folding-stats.json"
    with open(config_file, "r") as cfg:
        config = loads(cfg.read())

    # -----------------------------------------------------------
    # ----- Writing environment vars to js files
    # -----------------------------------------------------------
    logging.info("Checking Folding@Home team name...")
    # try to get Team ID (environment -> json -> error)
    teamid = os.environ.get("FAH_TEAMID", "")
    limitdays = os.environ.get("FAH_LIMITDAYS", "")
    milestone1 = os.environ.get("FAH_MILESTONE1", "")
    milestone2 = os.environ.get("FAH_MILESTONE2", "")
    milestone3 = os.environ.get("FAH_MILESTONE3", "")
    goal = os.environ.get("FAH_GOAL", "")
    pushrank_time = os.environ.get("FAH_PUSHRANK_TIME", "")

    try:
        pushrank_change = os.environ["FAH_PUSHRANK_CHANGE"]
        if pushrank_change != "1":
            pushrank_change = None
    except Exception:
        pushrank_change = None

    try:
        pushrank_force = os.environ["FAH_PUSHRANK_FORCE"]
        if pushrank_force != "1":
            pushrank_force = None
    except Exception:
        pushrank_force = None

    try:
        email_server = os.environ["FAH_EMAIL_SERVER"]
        email_port = os.environ["FAH_EMAIL_PORT"]
        email_from = os.environ["FAH_EMAIL_FROM"]
        email_password = os.environ["FAH_EMAIL_PASSWORD"]
        email_to = os.environ["FAH_EMAIL_TO"]

        # email_to_list = re.split(r'[, ]*',email_to)
        email_to_list = email_to.replace(",", " ").split()
        logging.info("Email settings set successfully!")
    except Exception:
        logging.info("Email settings not set!")
        email_server = None
        email_port = None
        email_from = None
        email_password = None
        email_to = None

    if not teamid.isdigit():
        # teamid=getconfig(config,"team","0")
        logging.error(
            "Environment var FAH_TEAM_ID missing or not numeric. Abort!"
        )
        # exits the program
        sys.exit(1)
    if not limitdays.isdigit():
        logging.warning(
            "Environment var FAH_LIMITDAYS not valid. Setting default value."
        )
        limitdays = 99999
    if not milestone1.isdigit():
        logging.warning(
            "Environment var FAH_MILESTONE1 not valid. Setting default value."
        )
        milestone1 = -1
    if not milestone2.isdigit():
        logging.warning(
            "Environment var FAH_MILESTONE2 not valid. Setting default value."
        )
        milestone2 = -1
    if not milestone3.isdigit():
        logging.warning(
            "Environment var FAH_MILESTONE3 not valid. Setting default value."
        )
        milestone3 = -1
    if not goal.isdigit():
        logging.warning(
            "Environment var FAH_GOAL not valid. Setting default value."
        )
        goal = 1

    url = getconfig(config, "baseurl", "") + str(teamid)
    myResponse = requests.get(url)

    # For successful API call, response code will be 200 (OK)
    if myResponse.ok:
        jStats = json.loads(myResponse.content)

    teamname = str(getconfig(jStats, "name", ""))

    logging.debug("Team ID   : %s", str(teamid))
    logging.debug("Team name : %s", str(getconfig(jStats, "name", "")))

    logging.info("Propagating team id and name (%s)" % (mypath + "/team.js"))
    with open(mypath + "/team.js", "w") as f:
        f.write("var team = {\n")
        f.write("id: " + str(getconfig(jStats, "team", "")) + ",\n")
        f.write("name: '" + str(getconfig(jStats, "name", "")) + "'\n")
        f.write("}")
    f.close()

    logging.info("Propagating settings (%s)" % (mypath + "/settings.js"))

    with open(mypath + "/settings.js", "w") as f:
        f.write("var settings = {\n")
        f.write("limitdays: " + str(limitdays) + ",\n")
        f.write("milestone1: " + str(milestone1) + ",\n")
        f.write("milestone2: " + str(milestone2) + ",\n")
        f.write("milestone3: " + str(milestone3) + ",\n")
        f.write("goal: " + str(goal) + "\n")
        f.write("}")
    f.close()

    # -----------------------------------------------------------

    logging.info("Checking Folding@Home stats...")
    uid_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pushrank_timestamp_now = datetime.datetime.now().strftime("%H%M")
    logging.debug("UID_DATETIME=%s", (uid_datetime))
    url = getconfig(config, "baseurl", "") + str(teamid)
    myResponse = requests.get(url)

    # For successful API call, response code will be 200 (OK)
    if myResponse.ok:
        jStats = json.loads(myResponse.content)

        # read rid file (old rank)
        rank_old = 0
        rank_new = 0
        try:
            with open(mypath + "/data/" + str(teamid) + ".rid", "r") as f:
                rank_old = f.readline()
                f.close()
            logging.debug("Previous rank : %s", (str(rank_old)))
        except IOError:
            logging.warning(
                "Could not read file: %s",
                (mypath + "/data/" + str(teamid) + ".rid"),
            )
            pass

        rank_new = getconfig(jStats, "rank", "0")
        logging.debug("Current rank  : %s", (rank_new))

        # write rid file (new rank (or old if not updated))
        rank_updated = False
        # rank id file
        with open(mypath + "/data/" + str(teamid) + ".rid", "w") as f:
            f.write(str(rank_new))
            f.close()

        if int(rank_new) != int(rank_old):
            rank_updated = True

        # update database/csv if rank was changed
        if rank_updated is True:
            logging.info("Rank changed (%s -> %s)", rank_old, rank_new)

            if getconfig(config, "database/sqlite", "") != "":
                # write database
                logging.debug("Rank changed. SQlite is being updated...")
                file_db = (
                    mypath + "/" + getconfig(config, "database/sqlite", "")
                )
                conn = sqlite3.connect(file_db)
                cur = conn.cursor()
                try:
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS stats(datetime TEXT, uid_datetime TEXT, team integer, rank integer, change)"
                    )
                except Exception:
                    logging.error("Faild to create sqlite3 table 'stats'")

                try:
                    cur.execute(
                        "CREATE VIEW IF NOT EXISTS view_stats AS SELECT datetime,uid_datetime,team,rank,(LAG ( rank, 1, 0 ) OVER (ORDER BY datetime) - rank ) change FROM stats"
                    )
                except Exception:
                    logging.error("Faild to create sqlite3 view 'view_stats'")

                try:
                    cur.execute(
                        'CREATE VIEW IF NOT EXISTS view_supporter AS SELECT s.uid_datetime,group_concat(t.name, ", ") as supporter FROM stats s, team t WHERE s.uid_datetime = t.uid_datetime AND t.supporter=1 GROUP BY s.uid_datetime'
                    )
                except Exception:
                    logging.error(
                        "Faild to create sqlite3 view 'view_supporter'"
                    )

                # Here we calculate the difference (change) of the rank in relation
                # to the row before as a backup.
                # The main calculation is done by the sqlite view 'view_stats' where
                # the difference is calculated by the LAG() function. Export is done
                # by exporting the view later where the difference is automatically
                # calculated!
                change_indicator = 0
                try:
                    cur.execute(
                        "select rank from stats ORDER by datetime DESC LIMIT 1"
                    )
                    record = cur.fetchone()
                    rank_old = record[0]
                    #                logging.debug("old db rank=%s" % (rank_old))
                    change_indicator = rank_old - rank_new
                    # new rank lower than the old rank
                    #                if change_indicator > 0:
                    #                    logging.debug("new rank < from db detected")
                    # new rank higher than the old rank
                    #                if change_indicator < 0:
                    #                    logging.debug("new rank > from db detected")
                except Exception:
                    # rank unchanged or invalid
                    change_indicator = 0

                try:
                    cur.execute(
                        "INSERT INTO stats VALUES(datetime('now', 'localtime'), '"
                        + uid_datetime
                        + "',"
                        + str(teamid)
                        + ", "
                        + str(rank_new)
                        + ","
                        + str(change_indicator)
                        + ")"
                    )
                except Exception:
                    logging.error(
                        "Faild to insert sqlite3 into table 'stats')"
                    )

                conn.commit()

                # getting team member stats (only if team rank is changed)
                logging.info("Getting team member stats...")
                for member in getconfig(jStats, "donors"):
                    member_name = member["name"]
                    logging.debug(
                        "Collecting team meber data of '%s'", str(member_name)
                    )
                    member_id = member["id"]
                    try:
                        member_rank = member["rank"]
                        sql_select_Query = "select credit from (select * from team where id=%s order by datetime DESC LIMIT 2) ORDER BY datetime ASC LIMIT 1"
                        cur = conn.cursor()
                        cur.execute(sql_select_Query, (str(member_id),))
                        record = cur.fetchone()

                        member_supporter = 0
                        member_credit = member["credit"]
                        member_old_credit = record[0]
                        logging.debug(
                            "checkin changed credits (old/new credits): %s => %s"
                            % (str(member_old_credit), str(member_credit))
                        )
                        if member_credit != member_old_credit:
                            member_supporter = 1
                        #                        logging.info("member IS A SUPPORTER of this rank change")
                        else:
                            member_supporter = 0
                    #                        logging.info("member is not a supporter of this rank change")
                    except Exception:
                        member_rank = 999999
                        member_supporter = 0

                    member_credit = member["credit"]
                    #                logging.info("%s (%s)", member_name, member_id)

                    try:
                        cur.execute(
                            "CREATE TABLE IF NOT EXISTS team(datetime TEXT, uid_datetime TEXT, team INTEGER, id INTEGER, name TEXT, rank integer, credit INTEGER, supporter INTEGER)"
                        )
                    except Exception:
                        logging.error("Faild to create sqlite3 view 'team')")

                    try:
                        cur.execute(
                            "INSERT INTO team VALUES(datetime('now', 'localtime'), '"
                            + uid_datetime
                            + "', "
                            + str(teamid)
                            + ", "
                            + str(member_id)
                            + ", '"
                            + str(member_name)
                            + "', "
                            + str(member_rank)
                            + ", "
                            + str(member_credit)
                            + ", "
                            + str(member_supporter)
                            + ")"
                        )
                    except Exception:
                        logging.error(
                            "Faild to insert sqlite3 into table 'team')"
                        )

                    conn.commit()

            #            # Close the connection
            #            conn.close()
            else:
                logging.debug("No CSV file given.")

            # write csv
            if getconfig(config, "database/csv", "") != "":
                logging.debug("Rank changed. CSV file is being updated...")

                # write csv if value is given
                file_csv = mypath + "/" + getconfig(config, "database/csv", "")

                # initialize csv header if file is not present
                #            logging.debug("filename: %s", (file_csv))
                cursor = conn.cursor()
                try:
                    cursor.execute("select * from view_stats")
                    with open(file_csv, "w") as csv_file:
                        csv_writer = csv.writer(csv_file, delimiter=",")
                        csv_writer.writerow([i[0] for i in cursor.description])
                        csv_writer.writerows(cursor)
                except Exception:
                    logging.error("Faild to read sqlite3 view 'view_stats')")
                    logging.error("Faild to propagate view data to CSV file)")

            else:
                logging.debug("No CSV file given.")

            # write csv
            if getconfig(config, "database/csv", "") != "":
                logging.debug("Rank changed. CSV file is being updated...")

                # write csv if value is given
                file_csv = (
                    mypath + "/" + getconfig(config, "database/supporter", "")
                )

                # initialize csv header if file is not present
                #            logging.debug("filename: %s", (file_csv))
                cursor = conn.cursor()
                try:
                    cursor.execute("select * from view_supporter")
                    with open(file_csv, "w") as csv_file:
                        csv_writer = csv.writer(csv_file, delimiter=",")
                        csv_writer.writerow([i[0] for i in cursor.description])
                        csv_writer.writerows(cursor)
                except Exception:
                    logging.error(
                        "Faild to read sqlite3 view 'view_supporter')"
                    )
                    logging.error(
                        "Faild to propagate supporter data to CSV file)"
                    )

            else:
                logging.debug("No CSV file given.")
        else:
            logging.debug("Rank unchanged (%s).", rank_new)
            pass

        rank_pushed = 0
        if pushrank_time == pushrank_timestamp_now:
            # notification at time
            rank_pushed = 1
            rank_push_mode = "time"
        else:
            # notification at change
            if pushrank_change == "1" and rank_updated is True:
                rank_pushed = 1
                rank_push_mode = "change"

        if pushrank_force == "1":
            # notification forced
            rank_pushed = 1
            rank_push_mode = "force"

        if rank_pushed == 1:
            logging.debug("Rank pushed. SQlite is being updated...")
            file_db = mypath + "/" + getconfig(config, "database/sqlite", "")
            conn = sqlite3.connect(file_db)
            cur = conn.cursor()
            try:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS rankpush(datetime TEXT, uid_datetime TEXT, team integer, mode TEXT, rank integer, delta integer)"
                )
            except Exception:
                logging.error("Faild to insert sqlite3 into table 'rankpush')")

            try:
                sql_select_Query = "SELECT rank FROM rankpush WHERE mode='%s' ORDER BY uid_datetime DESC LIMIT 1"
                cur = conn.cursor()
                try:
                    cur.execute(sql_select_Query, (rank_push_mode,))
                    record = cur.fetchone()
                    rank_old = 0
                    rank_old = record[0]
                except Exception:
                    rank_old = rank_new
                    logging.error("Faild to read sqlite3 table 'rank')")
            except Exception:
                # error determining value
                rank_old = rank_new

            # reverse rank delta (positive=rank up, negative=rank down)
            rank_delta = (rank_new - rank_old) * (-1)

            try:
                cur.execute(
                    "INSERT INTO rankpush VALUES(datetime('now', 'localtime'), '"
                    + uid_datetime
                    + "', "
                    + str(teamid)
                    + ", '"
                    + str(rank_push_mode)
                    + "', "
                    + str(rank_new)
                    + ", "
                    + str(rank_delta)
                    + ")"
                )
            except Exception:
                logging.error("Faild to insert sqlite3 into table 'rankpush')")

            conn.commit()

            email_subject = (
                "[FAH rank notification/"
                + rank_push_mode
                + "] '"
                + teamname
                + "': "
                + str(rank_new)
            )
            email_message = (
                "FAH rank for '"
                + teamname
                + "' - "
                + str(datetime.datetime.now().strftime("%d.%m.%Y"))
                + " at "
                + str(datetime.datetime.now().strftime("%H:%M"))
                + "h :\n\n"
                + str(rank_new)
                + "\n\n\nDelta to last mode based ("
                + rank_push_mode
                + ") measurement: \n\n"
                + str(rank_delta)
            )
            try:
                send_notification(email_subject, email_message)
            except Exception:
                logging.error(
                    "Sending rank notification (%s) failed!", rank_push_mode
                )
            logging.info(
                "Push rank (mode=%s, now=%s): %s (delta: %s)",
                rank_push_mode,
                pushrank_timestamp_now,
                rank_new,
                rank_delta,
            )

    else:
        # If response code is not ok (200), print the resulting http error code with description
        myResponse.raise_for_status()
