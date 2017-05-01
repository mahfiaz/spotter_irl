from .round import Round
from .helper import iterateZero
import game_config

from enum import Enum, auto

#def enum(*args):
#    enums = dict(zip(args, range(len(args))))
#    return type('Enum', (), enums)


#EventType = enum('didFlee', 'didSpot', 'didTouch', 'failedSpot', 'didSpotJailed', 'didSpotMate', 'wasSpotted', 'wasTouched', 'wasAdded', 'wasExposingSelf', 'wasAimedOldCode', 'obscureMessage', 'unregisteredMessage')

class EventType(Enum):
    didFlee = auto()
    didSpot = auto()
    didTouch = auto()
    failedSpot = auto()
    didSpotJailed = auto()
    didSpotMate = auto()
    wasSpotted = auto()
    wasTouched = auto()
    wasAdded = auto()
    wasExposingSelf = auto()
    wasAimedOldCode = auto()
    obscureMessage = auto()
    unregisteredMessage = auto()


class Event():

# init
    def initOnce(cursor):
        Event.cur = cursor
        Event._createDataTable()

    def _createDataTable():
        Event.cur.execute("""CREATE TABLE event_list (
            round_id int,
            player_id int,
            event_type int,
            extra_data VARCHAR(160) DEFAULT '',
            timestamp TIMESTAMP DEFAULT statement_timestamp() )""")

# add player events
    def addPlayer(playerId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type)
            VALUES (%s, %s, %s)""", (Round.getActiveId(), playerId, EventType.wasAdded.value))

    def addSpot(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Round.getActiveId(), hitterId, EventType.didSpot.value, Round.getActiveId(), victimId, EventType.wasSpotted.value))

    def addTouch(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Round.getActiveId(), hitterId, EventType.didTouch.value, Round.getActiveId(), victimId, EventType.wasTouched.value))

    def addSpotMate(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Round.getActiveId(), hitterId, EventType.didSpotMate.value, Round.getActiveId(), victimId, EventType.wasSpotted.value))

    def addFailedSpot(hitterId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), hitterId, EventType.failedSpot.value, code))

    def addWasAimedWithOldCode(victimId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), victimId, EventType.wasAimedOldCode.value, code))

    def addAlreadyJailedSpot(hitterId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), victimId, EventType.didSpotJailed.value, code))

    def addFlee(playerId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type)
            VALUES (%s, %s, %s)""", (Round.getActiveId(), playerId, EventType.didFlee.value))

    def addExposeSelf(victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s)""", (Round.getActiveId(), victimId, EventType.wasExposingSelf.value))

    def addObscureMessage(playerId, message):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), playerId, EventType.obscureMessage.value, message))

    def addUnregisteredMessage(mobile, message):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), mobile, EventType.unregisteredMessage.value, message))

# get player state
    def isPlayerJailed(playerId):
        Event.cur.execute("""SELECT event_type
            FROM event_list
            WHERE player_id = %s
            ORDER BY timestamp DESC""", [playerId])
        event = Event.cur.fetchall()
        if event:
            ev = event[0][0]
            return ev == EventType.wasSpotted.value or ev == EventType.wasTouched.value or ev == EventType.wasExposingSelf.value or ev == EventType.wasAdded.value
        return True

    def getPlayerLastActivity(playerId):
        Event.cur.execute("""SELECT timestamp
            FROM event_list
            WHERE player_id = %s
            ORDER BY timestamp DESC""", [playerId])
        timestamp = Event.cur.fetchall()
        if timestamp:
            return timestamp[0][0]

    def _getPlayerLastFleeingTime(playerId):
        Event.cur.execute("""SELECT timestamp
            FROM event_list
            WHERE (player_id = %s AND event_type = %s)
            ORDER BY timestamp DESC""", (playerId, EventType.didFlee.value))
        timestamp = Event.cur.fetchall()
        if timestamp:
            return timestamp[0]


# get player stats
    def getPlayerSpotTotalCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s) AND round_id = %s)""",
            (playerId, EventType.didSpot.value, EventType.didTouch.value, roundId))
        return iterateZero(Event.cur.fetchone())

    def getPlayerTouchCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type = %s AND round_id = %s)""",
            (playerId, EventType.didTouch.value, roundId))
        return iterateZero(Event.cur.fetchone())

    def getPlayerJailedCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s, %s) AND round_id = %s)""",
            (playerId, EventType.wasSpotted.value, EventType.wasTouched.value, EventType.wasExposingSelf.value, roundId))
        return iterateZero(Event.cur.fetchone())

    def getPlayerDisloyalityCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s) AND round_id = %s)""",
            (playerId, EventType.didSpotMate.value, EventType.wasExposingSelf.value, roundId))
        return iterateZero(Event.cur.fetchone())

# get event list

    # Event pairs in eventList
    #didFlee
    #didSpot         wasSpotted
    #didTouch        wasTouched
    #didSpotMate     wasSpotted
    #??     wasExposingSelf

    def getEventListRaw(roundId, rows):
        Event.cur.execute("""SELECT event_type, player_id, timestamp
            FROM event_list
            WHERE round_id = %s AND event_type IN (%s, %s, %s, %s)
            ORDER BY timestamp DESC""", (roundId, EventType.didFlee.value, EventType.didSpot.value, EventType.didTouch.value, EventType.didSpotMate.value))
        return Event.cur.fetchmany(rows)

    def getDidEventPair(type, timestamp):
        if not (type == EventType.didSpot.value or type == EventType.didTouch.value or type == EventType.didSpotMate.value):
            return
        expectedEvent = EventType.wasSpotted.value
        if type == EventType.didTouch.value:
            expectedEvent = EventType.wasTouched.value
        Event.cur.execute("""SELECT player_id
            FROM event_list
            WHERE timestamp = %s AND event_type = %s""", (timestamp, expectedEvent))
        return iterateZero(Event.cur.fetchone())

