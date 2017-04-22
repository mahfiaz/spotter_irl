import random

class Code:

    def initOnce(cursor):
        Code.cur = cursor
        Code.createDataTable()

    def createDataTable():
        Code.cur.execute("""CREATE TABLE shot_code (
            shot_id serial PRIMARY KEY,
            shot_value int unique,
            player_id int,
            added timestamp DEFAULT statement_timestamp())""")

    def getOwnerId(code):
        Code.cur.execute("""SELECT player_id
            FROM shot_code
            WHERE shot_value = %s""", [code])
        return Code.cur.fetchone()

    def getCodeIdByPlayerId(playerId):
        Code.cur.execute("""SELECT player_shot_id
            FROM player_data
            WHERE player_id = %s""", [playerId])
        return Code.cur.fetchone()

    def getShotId(code):
        Code.cur.execute("""SELECT shot_id
            FROM shot_code
            WHERE shot_value = %s""", [code])
        return Code.cur.fetchone()

    def getCodeById(shotId):
        Code.cur.execute("""SELECT shot_value
            FROM shot_code
            WHERE shot_id = %s""", [shotId])
        return Code.cur.fetchone()

    def generateNewShotCode(playerId):
        fail = True
        while fail:
            newCode = random.randint(1000,9999)
            fail = Code.getOwnerId(newCode)
        Code.cur.execute("""INSERT INTO shot_code (shot_value, player_id)
            VALUES (%s, %s)""", (newCode, playerId))
        newShotId = Code.getShotId(newCode)
        Code.cur.execute("""UPDATE player_data
            SET player_shot_id = %s
            WHERE player_id = %s""", (newShotId, playerId))
        return newShotId
