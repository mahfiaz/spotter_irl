#!/usr/bin/env python3

import psycopg2
import datetime
import time
import random
import game_config

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *


def connectDB():
    database, host = (game_config.connection_dbname, game_config.connection_host)
    user, password = (game_config.connection_user, game_config.connection_password)
    connParams = "dbname='" + database + "' user='" + user + "' host='" + host + "' password='" + password + "'"
    try:
        connection = psycopg2.connect(connParams)
        return connection
    except:
        print ("Error. Unable to connect to the database. If losing data is acceptable, try running 'python reset_db.py'")
        return False







def main():
    connection = connectDB()
    if not connection:
        return
    cursor = connection.cursor()

    Round.initOnce(cursor)
    Player.initOnce(cursor)
    Code.initOnce(cursor)
    Team.initOnce(cursor)
    Event.initOnce(cursor)

    Round.addTestRounds()
    Player.addTestPlayers()
    Player.add("Vollts2", "3593", "ille2@gmail.ocom")

    Round.print()
    print("round active", Round.isActive())
    Player.print()

    Team.addTestTeams()
    Team.addPlayersToTeams()
    Team.getTeamsList()

#    Event.addTestEvents()
    Action.addTestAction()


if __name__ == "__main__":
    main()

#TODO
# respawning implementation
# timestamps and ascending-descending sorting not working.