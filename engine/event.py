from .round import Round

def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)


EventType = enum('didFlee', 'didSpot', 'didTouch', 'failedSpot', 'didSpotJailed', 'didSpotMate', 'wasSpotted', 'wasTouched', 'wasAdded', 'wasExposingSelf', 'wasAimedOldCode', 'obscureMessage', 'unregisteredMessage')

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
            VALUES (%s, %s, %s)""", (Round.getActiveId(), playerId, EventType.wasAdded))

    def addSpot(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Round.getActiveId(), hitterId, EventType.didSpot, Round.getActiveId(), victimId, EventType.wasSpotted))

    def addTouch(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Round.getActiveId(), hitterId, EventType.didTouch, Round.getActiveId(), victimId, EventType.wasTouched))

    def addSpotMate(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Round.getActiveId(), hitterId, EventType.didSpotMate, Round.getActiveId(), victimId, EventType.wasSpotted))

    def addFailedSpot(hitterId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), hitterId, EventType.failedSpot, code))

    def addWasAimedWithOldCode(victimId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), victimId, EventType.wasAimedOldCode, code))

    def addAlreadyJailedSpot(hitterId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), victimId, EventType.didSpotJailed, code))

    def addFlee(playerId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type)
            VALUES (%s, %s, %s)""", (Round.getActiveId(), playerId, EventType.didFlee))

    def addExposeSelf(victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s)""", (Round.getActiveId(), victimId, EventType.wasExposingSelf))

    def addObscureMessage(playerId, message):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), playerId, EventType.obscureMessage, message))

    def addUnregisteredMessage(mobile, message):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Round.getActiveId(), mobile, EventType.unregisteredMessage, message))

# get player state
    def isPlayerJailed(playerId):
        Event.cur.execute("""SELECT event_type
            FROM event_list
            WHERE player_id = %s
            ORDER BY timestamp DESC""", [playerId])
        event = Event.cur.fetchall()
        if event:
            ev = event[0][0]
            return ev == EventType.wasSpotted or ev == EventType.wasTouched or ev == EventType.wasExposingSelf or ev == EventType.wasAdded
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
            ORDER BY timestamp DESC""", (playerId, EventType.didFlee))
        timestamp = Event.cur.fetchall()
        if timestamp:
            return timestamp[0]


# get player stats
    def getPlayerSpotTotalCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s) AND round_id = %s)""",
            (playerId, EventType.didSpot, EventType.didTouch, roundId))
        return Event.cur.fetchone()[0]

    def getPlayerTouchCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type = %s AND round_id = %s)""",
            (playerId, EventType.didTouch, roundId))
        return Event.cur.fetchone()[0]

    def getPlayerJailedCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s, %s) AND round_id = %s)""",
            (playerId, EventType.wasSpotted, EventType.wasTouched, EventType.wasExposingSelf, roundId))
        return Event.cur.fetchone()[0]

    def getPlayerDisloyalityCount(playerId, roundId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s) AND round_id = %s)""",
            (playerId, EventType.didSpotMate, EventType.wasExposingSelf, roundId))
        return Event.cur.fetchone()[0]

    def getSpottingAccuracy(playerId, roundId):
        success = Event.getPlayerSpotTotalCount(playerId, roundId)
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s, %s, %s, %s, %s) AND round_id = %s)""",
            (playerId, EventType.didSpot, EventType.didSpotJailed, EventType.didTouch,
            EventType.failedSpot, EventType.didSpotMate, EventType.wasExposingSelf, roundId))
        all = Event.cur.fetchone()[0]
        if all:
            return success / all
        return 0

