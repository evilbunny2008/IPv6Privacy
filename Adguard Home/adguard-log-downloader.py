#!/usr/bin/python3

import datetime
import json
import pymysql
import requests
import time

from dateutil import parser
from zoneinfo import ZoneInfo

# Config Section

ADGUARD_URL = "https://router.example.com:8443/control/querylog"
ADGUARD_USER = "adguard-username"
ADGUARD_PASS = "adguard-password"

DB = {
    "host": "localhost",
    "user": "database-username",
    "password": "database-password",
    "database": "database-name",
    "autocommit": True
}

ADGUARD_PAGE_LIMIT = 500

# Nothing is configurable below this line

local_tz = datetime.datetime.now().astimezone().tzinfo

def db_connect():
    return pymysql.connect(**DB)

def get_last_timestamp(db):
    with db.cursor() as c:
        c.execute("SELECT v FROM state WHERE k='last_ts'")
        row = c.fetchone()
        return row[0] if row else None

def set_last_timestamp(db, ts):
    with db.cursor() as c:
        c.execute(
            """
            INSERT INTO state (k, v)
            VALUES ('last_ts', %s)
            ON DUPLICATE KEY UPDATE v = VALUES(v)
            """,
            (ts,)
        )

def fetch_page(before=None):
    params = {"limit": ADGUARD_PAGE_LIMIT}
    params["response_status"] = "all"

    if before:
        params["older_than"] = before

    r = requests.get(
        ADGUARD_URL,
        auth=(ADGUARD_USER, ADGUARD_PASS),
        params=params,
        timeout=10
    )

    r.raise_for_status()
    return r.json()

def main():
    db = db_connect()
    last_ts = get_last_timestamp(db)

    before = None
    newest_seen = last_ts

    while True:
        resp = fetch_page(before)
        data = resp.get("data", [])

        if not data:
            break

        oldest = None

        with db.cursor() as c:
            for e in data:
                answers = e.get("answer", [])

                if not answers:
                    continue

                ts = e.get("time")
                if not ts:
                    continue

                dt_utc = parser.isoparse(ts)

                dt_local = dt_utc.astimezone(local_tz)

                answers_json = json.dumps(answers)
                hostname = e.get("question").get("name")
                client = e.get("client")
                qtype = e.get("question").get("type")
                reason = e.get("reason")
                status = e.get("status")
                rule = e.get("rule")
                ruleid = 0

                blocked = 0
                if rule:
                    rules = e.get("rules", [])
                    if rules:
                        ruleid = int(rules[0].get("filter_list_id", 0))

                    if not rule.startswith("@@"):
                        blocked = 1

                c.execute("""
                    INSERT IGNORE INTO querylog
                    (time, hostname, client, qtype, answers, blocked, rule, ruleid)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    dt_local,
                    hostname,
                    client,
                    qtype,
                    answers_json,
                    blocked,
                    rule,
                    ruleid
                ))

                newest_seen = max(newest_seen, ts)
                oldest = ts if oldest is None or ts < oldest else oldest

        before = oldest

        if oldest <= last_ts:
            break

    if newest_seen != last_ts:
        set_last_timestamp(db, newest_seen)

    db.close()

if __name__ == "__main__":
    main()
