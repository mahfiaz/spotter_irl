#!/usr/bin/env python3

import configparser
import os
import psycopg2

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *

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
    if not os.path.isfile('config.ini'):
        import shutil
        shutil.copyfile('config-default.ini', 'config.ini')
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Connect to database
    try:
        db = config['database']
        parameters = "host='%s' dbname='%s' user='%s' password='%s'" % (
            db['host'], db['dbname'], db['user'], db['password'])
        connection = psycopg2.connect(parameters)
        connection.set_session(autocommit=True)
        cursor = connection.cursor()
    except:
        print ("Error. Unable to connect to the database. If losing data is acceptable, try running 'python reset_db.py'")
        exit()
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
