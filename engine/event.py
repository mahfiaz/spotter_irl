def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)


EventType = enum('spawn', 'wasHit', 'wasHeadshotted', 'didHit', 'didHeadshot', 'missedHit', 'alreadyDead', 'didHitTeamMate', 'strangeSms')

class Event():
    currentRoundId = 0

    def initOnce(cursor):
        Event.cur = cursor
        Event.createDataTable()

    def createDataTable():
        Event.cur.execute("""CREATE TABLE event_list (
            round_id int,
            player_id int,
            event_type int,
            extra_data VARCHAR(160) DEFAULT '',
            timestamp TIMESTAMP)""")

    def roundId():
        return Event.currentRoundId

    def setRoundId(roundId):
        Event.currentRoundId = roundId

    def addHit(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Event.roundId(), hitterId, EventType.didHit, Event.roundId(), victimId, EventType.wasHit))

    def addHeadshot(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Event.roundId(), hitterId, EventType.didHeadshot, Event.roundId(), victimId, EventType.wasHeadshotted))

    def addHitTeamMate(hitterId, victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s), (%s, %s, %s)""", (Event.roundId(), hitterId, EventType.didHitTeamMate, Event.roundId(), victimId, EventType.wasHit))

    def addMissedHit(hitterId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Event.roundId(), hitterId, EventType.missedHit, code))

    def addAlreadyDeadHit(hitterId, code):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
            VALUES (%s, %s, %s, %s)""", (Event.roundId(), hitterId, EventType.alreadyDead, code))

    def addSpawn(spawnerId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type)
            VALUES (%s, %s, %s, %s)""", (Event.roundId(), spawnerId, EventType.spawn))

    def addSuicide(victimId):
        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type) 
            VALUES (%s, %s, %s)""", (Event.roundId(), victimId, EventType.wasHit))


#    def addStrangeSms(number, message):
#        Event.cur.execute("""INSERT INTO event_list (round_id, player_id, event_type, extra_data)
#            VALUES (%s, %s, %s, %s)""", (Event.roundId(), number, EventType.strangeSms, message))

    def getPlayerDidHitCuont(playerId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type = %s)""",
            (playerId, EventType.didHit))
        return Event.cur.fetchone()

    def getPlayerDidTotalHitCuont(playerId):
        Event.cur.execute("""SELECT COUNT(*) AS event_type
            FROM event_list
            WHERE (player_id = %s AND event_type IN (%s, %s))""",
            (playerId, EventType.didHit, EventType.didHeadshot))
        return Event.cur.fetchone()

    def addTestEvents():
        Event.setRoundId(1)
        Event.addHit(2, 3)
        Event.addHeadshot(3, 2)
        Event.addHeadshot(2, 4)
        Event.addMissedHit(1, 6956)
        Event.addAlreadyDeadHit(1, 3392)
        Event.addHitTeamMate(1, 2)
        Event.addHit(2, 4)
        print("event test",Event.getPlayerDidHitCuont(2), Event.getPlayerDidTotalHitCuont(2))