import datetime
import time
from threading import Timer

import game_config
from .helper import iterateZero

dateformat = game_config.database_dateformat

class Round():
    _activeId = 0
    _callRoundStarted = None
    _callRoundEnding = None
    _callRoundEnded = None
    
# init
    def initOnce(cursor):
        Round.cur = cursor
        Round._createDataTable()

    def _createDataTable():
        Round.cur.execute("""CREATE TABLE round_data (
            round_id serial PRIMARY KEY,
            round_name VARCHAR(30) NOT NULL,
            round_start TIMESTAMP,
            round_end TIMESTAMP)""")

# modify
    def add(name, time_start, time_end):
        Round.cur.execute("""SELECT round_name
            FROM round_data 
            WHERE (round_start = %s OR (round_start < %s AND round_end > %s)) OR
            (round_end = %s AND (round_start < %s AND round_end > %s))""",
            (time_start, time_start, time_start, time_end, time_end, time_end))
        if not Round.cur.fetchone():
            Round.cur.execute("""INSERT INTO round_data (round_name, round_start, round_end)
                VALUES (%s, %s, %s)""", (name, time_start, time_end))
            return True
        else:
            print("Error: New round has overlapping time. not added", name, time_start, time_end)

# state
    def getActiveId():
        return Round._activeId

    def isActive():
        if Round.getActiveId():
            return True
        else:
            return False

    def existingId(roundId):
        Round.cur.execute("""SELECT round_id
            FROM round_data 
            WHERE round_id = %s""", [roundId])
        if Round.cur.fetchone():
            return True

    def getName(roundId):
        Round.cur.execute("""SELECT round_name
            FROM round_data 
            WHERE round_id = %s""", [roundId])
        return iterateZero(Round.cur.fetchone())


# round time
#    def getActiveSecondsLeft():
#        ends = Round._getEndTimeOfActive()
#        if ends:
#            return (ends - datetime.datetime.now()).total_seconds()

    def _getStartTimeOfNext():
        Round.cur.execute("""SELECT round_start
            FROM round_data 
            WHERE (round_start > statement_timestamp())
            ORDER BY round_start ASC""")
        return iterateZero(Round.cur.fetchone())

    def _getEndTimeOfActive():
        Round.cur.execute("""SELECT round_end
            FROM round_data 
            WHERE round_id = %s""", [Round.getActiveId()])
        return iterateZero(Round.cur.fetchone())

    def getStartTime(id):
        Round.cur.execute("""SELECT round_start
            FROM round_data 
            WHERE round_id = %s""", (id,))
        return iterateZero(Round.cur.fetchone())

    def getEndTime(id):
        Round.cur.execute("""SELECT round_end
            FROM round_data 
            WHERE round_id = %s""", (id,))
        return iterateZero(Round.cur.fetchone())

# round automatic restarting and finishing
    def updateActiveId():
        Round.cur.execute("""SELECT round_id
            FROM round_data 
            WHERE (round_start <= statement_timestamp() AND round_end > statement_timestamp())""")
        activeId = iterateZero(Round.cur.fetchone())
        Round._checkRoundChange(activeId)
        return Round._activeId

    def _checkRoundChange(newActiveId):
        if Round._activeId != newActiveId:
            if Round.existingId(newActiveId):
                Round._roundStart(newActiveId)
            else:
                Round._roundEnd()

    def _roundEnd():
        next = Round._getStartTimeOfNext()
        if next:
            delay = next - datetime.datetime.now()
            Timer(delay.total_seconds() + 1, Round._roundStartCall, ()).start()

    def _roundStart(newActiveId):
        Round._activeId = newActiveId
        ends = Round._getEndTimeOfActive()
        early5 = ends - datetime.timedelta(seconds = 2)
        early1 = ends - datetime.timedelta(seconds = 1)
        if datetime.datetime.now() < early5:
            Timer((early5 - datetime.datetime.now()).total_seconds(), Round._minutesLeftCall, (2,)).start()
        if datetime.datetime.now() < early1:
            Timer((early1 - datetime.datetime.now()).total_seconds(), Round._minutesLeftCall, (1,)).start()
        if datetime.datetime.now() < ends:
            Timer((ends - datetime.datetime.now()).total_seconds(), Round._roundOverCall, ()).start()

# callbacks
    def setCallbacks(roundStarted, roundEnding, roundEnded):
        Round._callRoundStarted = roundStarted
        Round._callRoundEnding = roundEnding
        Round._callRoundEnded = roundEnded

    def _roundStartCall():
        Round.updateActiveId()
        if Round._callRoundStarted:
            Round._callRoundStarted()

    def _minutesLeftCall(left):
        if Round._callRoundEnding:
            Round._callRoundEnding(left)

    def _roundOverCall():
        Round.updateActiveId()
        if Round._callRoundEnded:
            Round._callRoundEnded()

# print
    def print():
        Round.cur.execute("""SELECT round_id, round_name, round_start, round_end
            FROM round_data """)
        rows = Round.cur.fetchall()
        active = Round.getActiveId()
        print("Rounds:")
        for row in rows:
            id, name, time1, time2 = row
            indicator = " - "
            if id == active:
                indicator = " * "
            print(indicator, id, name, time1, time2)

