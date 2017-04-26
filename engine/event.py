def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)


EventType = enum('didFlee', 'didSpot', 'didTouch', 'failedSpot', 'didSpotJailed', 'didSpotMate', 'wasSpotted', 'wasTouched', 'wasAdded', 'wasExposingSelf', 'obscureMessage', 'unregisteredMessage')

class Event():
    currentRoundId = 0

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

    def _roundId():
        return Event.currentRoundId

    def setRoundId(roundId):
        Event.currentRoundId = roundId

    def addPlayer(playerId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type)
            VALUES (%s, %s, %s)""", (Event._roundId(), playerId, EventType.wasAdded))

    def addSpot(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Event._roundId(), hitterId, EventType.didSpot, Event._roundId(), victimId, EventType.wasSpotted))

    def addTouch(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Event._roundId(), hitterId, EventType.didTouch, Event._roundId(), victimId, EventType.wasTouched))

    def addSpotMate(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Event._roundId(), hitterId, EventType.didSpotMate, Event._roundId(), victimId, EventType.wasSpotted))

    def addFailedSpot(hitterId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Event._roundId(), hitterId, EventType.failedSpot, code))

    def addAlreadyJailedSpot(hitterId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Event._roundId(), hitterId, EventType.didSpotJailed, code))

    def addFlee(playerId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type)
            VALUES (%s, %s, %s)""", (Event._roundId(), playerId, EventType.didFlee))

    def addExposeSelf(victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s)""", (Event._roundId(), victimId, EventType.wasExposingSelf))

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

    def addObscureMessage(playerId, message):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Event._roundId(), playerId, EventType.obscureMessage, message))

    def addUnregisteredMessage(mobile, message):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Event._roundId(), mobile, EventType.unregisteredMessage, message))

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

    def getPlayerLastActivity(playerId):
        Event.cur.execute("""SELECT timestamp
            FROM event_list
            WHERE player_id = %s
            ORDER BY timestamp DESC""", [playerId])
        timestamp = Event.cur.fetchall()
        if timestamp:
            return timestamp[0][0]

    def addTestEvents(roundId):
        Event.setRoundId(roundId)
        Event.addSpot(2, 3)
        Event.addTouch(3, 2)
        Event.addTouch(2, 4)
        Event.addFailedSpot(1, 6956)
        Event.addAlreadyJailedSpot(1, 3392)
        Event.addSpotMate(1, 2)
        Event.addSpot(2, 4)
        print("event test allSpots/Touches",Event.getPlayerSpotTotalCount(2, Event._roundId()), Event.getPlayerTouchCount(2, Event._roundId()))
