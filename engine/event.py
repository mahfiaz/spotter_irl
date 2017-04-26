def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)


EventType = enum('didFlee', 'didSpot', 'didTouch', 'failedSpot', 'didSpotJailed', 'didSpotMate', 'wasSpotted', 'wasTouched', 'wasAdded', 'wasExposingSelf', 'obscureMessage')

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

#    def addoObscureMessage(number, message):
#        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
#            VALUES (%s, %s, %s, %s)""", (Event._roundId(), number, EventType.obscureMessage, message))

    def getPlayerSpotCount(playerId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type = %s)""",
            (playerId, EventType.didSpot))
        return Event.cur.fetchone()[0]

    def getPlayerTouchCount(playerId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s))""",
            (playerId, EventType.didSpot, EventType.didTouch))
        return Event.cur.fetchone()[0]

#    def getPlayerJailedCount(playerId):

#    def getPlayerDisloyalityCount(playerId):


    def addTestEvents():
        Event.setRoundId(1)
        Event.addSpot(2, 3)
        Event.addTouch(3, 2)
        Event.addTouch(2, 4)
        Event.addFailedSpot(1, 6956)
        Event.addAlreadyJailedSpot(1, 3392)
        Event.addSpotMate(1, 2)
        Event.addSpot(2, 4)
        print("event test spots/Touches",Event.getPlayerSpotCount(2), Event.getPlayerTouchCount(2)) 