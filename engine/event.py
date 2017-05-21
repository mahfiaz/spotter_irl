from .round import Round
from .helper import iterateZero
import game_config

from enum import Enum   

#def enum(*args):
#    enums = dict(zip(args, range(len(args))))
#    return type('Enum', (), enums)


#EventType = enum('didFlee', 'didSpot', 'didTouch', 'failedSpot', 'didSpotJailed', 'didSpotMate', 'wasSpotted', 'wasTouched', 'wasAdded', 'wasExposingSelf', 'wasAimedOldCode', 'obscureMessage', 'unregisteredMessage')

class EventType(Enum):
    didFlee = 1
    didSpot = 2
    didTouch = 3
    failedSpot = 4
    didSpotJailed = 5
    didSpotMate = 6
    wasSpotted = 7
    wasTouched = 8
    wasAdded = 9
    wasAddedToTeam = 10
    wasExposingSelf = 11
    wasAimedOldCode = 12
    obscureMessage = 13
    unregisteredMessage = 14
    teamChat = 15


class Event:

# init
    def initDB(cursor):
        Event.cur = cursor
        Event._createDataTable()

    def initConnect(cursor):
        Event.cur = cursor

    def _createDataTable():
        Event.cur.execute("""DROP TABLE IF EXISTS event_list""")
        Event.cur.execute("""CREATE TABLE event_list (
            round_id int,
            player_id int,
            team_id_visible int DEFAULT 0,
            event_type int,
            extra_data VARCHAR(160) DEFAULT '',
            timestamp TIMESTAMP DEFAULT statement_timestamp() )""")

# add player events
    def addPlayer(playerId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type)
            VALUES (%s, %s, %s)""", (Round.getActiveId(), playerId, EventType.wasAdded.value))

    def addPlayerToTeam(playerId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type)
            VALUES (%s, %s, %s)""", (Round.getActiveId(), playerId, EventType.wasAddedToTeam.value))

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

    def addChatMessage(playerId, teamId, message):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, team_id_visible, event_type, extra_data)
            VALUES (%s, %s, %s, %s, %s)""", (Round.getActiveId(), playerId, teamId, EventType.teamChat.value, message))



# get player state
    def isPlayerJailed(playerId):
        Event.cur.execute("""SELECT event_type
            FROM event_list
            WHERE player_id = %s
            ORDER BY timestamp DESC""", [playerId])
        event = Event.cur.fetchall()
        if event:
            ev = event[0][0]
            return ev == EventType.wasSpotted.value or ev == EventType.wasTouched.value or ev == EventType.wasExposingSelf.value or ev == EventType.wasAdded.value or ev == EventType.wasAddedToTeam.value
        return True

    def getPlayerLastActivity(playerId):
        Event.cur.execute("""SELECT timestamp
            FROM event_list
            WHERE player_id = %s
            ORDER BY timestamp DESC""", [playerId])
        timestamp = Event.cur.fetchall()
        if timestamp:
            return timestamp[0][0]

    def getPlayerLastActivityFormatted(playerId):
        time = Event.getPlayerLastActivity(playerId)
        if time:
            return time.strftime(game_config.database_dateformat)


    def _getPlayerLastFleeingTime(playerId):
        Event.cur.execute("""SELECT timestamp
            FROM event_list
            WHERE (player_id = %s AND event_type = %s)
            ORDER BY timestamp DESC""", (playerId, EventType.didFlee.value))
        timestamp = Event.cur.fetchall()
        if timestamp:
            return timestamp[0][0]


# get player stats
    def getPlayerSpotCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type = %s AND round_id = %s)""",
            (playerId, EventType.didSpot.value, roundId))
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
        Event.cur.execute("""SELECT event_type, player_id, timestamp, team_id_visible, extra_data
            FROM event_list
            WHERE round_id = %s AND event_type IN (%s, %s, %s, %s, %s, %s)
            ORDER BY timestamp DESC LIMIT 30""", (roundId, EventType.didFlee.value, EventType.didSpot.value, EventType.didTouch.value, EventType.didSpotMate.value, EventType.wasAddedToTeam.value, EventType.teamChat.value))
        return Event.cur.fetchmany(rows)

    def getDidEventPair(evType, timestamp):
        assert type(evType) == type(EventType.didSpot.value)
        if not (evType == EventType.didSpot.value or evType == EventType.didTouch.value or evType == EventType.didSpotMate.value):
            return
        expectedEvent = EventType.wasSpotted.value
        if evType == EventType.didTouch.value:
            expectedEvent = EventType.wasTouched.value
        Event.cur.execute("""SELECT player_id
            FROM event_list
            WHERE timestamp = %s AND event_type = %s""", (timestamp, expectedEvent))
        return iterateZero(Event.cur.fetchone())

