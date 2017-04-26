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



def processInput():
    userText = input("Enter command [spot] [flee]: ")
    if 'flee' in userText:
        id = input("enter id: ")
        if Player.getNameById(id):
            Action._flee(id)
            Player.printDetailed()
    if 'spot' in userText:
        mobile = input("enter mobile: ")
        code = input("enter code: ")
        Action.handleCode(mobile, code)
        Player.printDetailed()

def main():
    connection = connectDB()
    if not connection:
        return
    cursor = connection.cursor()

    Action.initAllOnce(cursor)

    Round.addTestRounds()
    Player.printDetailed()
    Action.addTestPlayers()
    Player.printDetailed()

    Round.print()
    print("round active", Round.isActive())

    Action.addTestTeams()
    Action.addPlayersToTeams()
    Team.getTeamsIdNameList(Round.getActiveId())

    Event.addTestEvents(Round.getActiveId())

    Action.addTestAction()

    print(Action.getAllStats(Round.getActiveId()))
    #Action.addTestAction2()

#    while True:
#        processInput()



if __name__ == "__main__":
    main()

#TODO
# private members _underscore
# if new round starts - start it at event too Event.setRoundId
# get full team stats as JSON. Saved in file
# return variables some are duples (var,)
# event analysis on rounds