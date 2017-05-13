#!/usr/bin/env python3

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass
import game_config
import subprocess

localPassword = getpass.getpass()
localUser = getpass.getuser()

localDBname = "postgres"
localHost = "localhost"

try:
    con = psycopg2.connect("dbname='" + localDBname + "' user='" + localUser + "' host='" + localHost + "' password='" + localPassword + "'")
except:
    subprocess.check_call("pg_ctl -D /usr/local/var/postgres start", shell=True)
    con = psycopg2.connect("dbname='" + localDBname + "' user='" + localUser + "' host='" + localHost + "' password='" + localPassword + "'")
#    print("""Error. Database is probably not running. start it by e.g. running 'pg_ctl -D /usr/local/var/postgres start'""")

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()

database, host = (game_config.connection_dbname, game_config.connection_host)
user, password = (game_config.connection_user, game_config.connection_password)

cur.execute("DROP DATABASE IF EXISTS " + database)
cur.execute("DROP USER IF EXISTS " + user)

cur.execute("CREATE USER " + user + " WITH PASSWORD '" + password + "'")
cur.execute("CREATE DATABASE " + database)

cur.close()
con.close()