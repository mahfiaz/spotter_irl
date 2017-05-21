#!/usr/bin/env python3

import os

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *

import connect
from game_config import file_events, file_stats, master_player

def addMasterPlayer():
    Action.addPlayer(master_player['name'], master_player['mobile'], '')

def addTestRoundsNormal():
    time.strftime(dateformat)
    time3 = format(datetime.datetime.now() + datetime.timedelta(seconds = -2), dateformat)
    time4 = format(datetime.datetime.now() + datetime.timedelta(seconds = 100 * 60), dateformat)
    #time5 = format(datetime.datetime.now() + datetime.timedelta(seconds = 120 * 60), dateformat)
    #time6 = format(datetime.datetime.now() + datetime.timedelta(seconds = 200 * 60), dateformat)

    Round.add("third", time3, time4)
    #Round.add("fourth", time5, time6)
    Round.updateActiveId()

def initGame():
    connection = connect.connectDB()
    if not connection:
        return
    cursor = connection.cursor()
    Action.initAllDB(cursor)
#    Round.addRealRounds()
    addTestRoundsNormal()
    addMasterPlayer()

    Round.print()

    Action.addTeamsToAllRounds()

# remove these
#    Action.addTestPlayers()
#    Stats.printPlayersDetailed()

    try:
        os.remove(file_events)
        os.remove(file_stats)
    except OSError:
        pass

if __name__ == "__main__":
    initGame()
