import random


from .event import Event

class Player:

    def initOnce(cursor):
        Player.cur = cursor
        Player._createDataTable()

    def _createDataTable():
        Player.cur.execute("""CREATE TABLE player_data (
            player_id serial PRIMARY KEY,
            player_name varchar(128) UNIQUE,
            player_mobile varchar(64) UNIQUE,
            player_email varchar(128) UNIQUE,
            player_code_id int DEFAULT 0,
            player_fleeing_code int DEFAULT 0,
            player_created timestamp DEFAULT statement_timestamp() )""")

    def add(name, mobile, email):
        Player.cur.execute("""SELECT player_name, player_mobile, player_email
            FROM player_data 
            WHERE player_name = %s OR player_mobile = %s OR player_email = %s""",
            (name, mobile, email))
        rows = Player.cur.fetchall()
        if not rows:
            Player.cur.execute("""INSERT INTO player_data (player_name, player_mobile, player_email) VALUES (%s, %s, %s)""", (name, mobile, email))
            print("Player added.", name, mobile, email)
            newId = Player.getIdByName(name)
            Player._generateFleeingCode(newId)
            return newId
        else:
            print("Error.", name ,"not entirely unique player. Not added!")

    def getIdByName(playerName):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_name = %s""", [playerName])
        return Player.cur.fetchone()

    def getNameById(playerId):
        Player.cur.execute("""SELECT player_name FROM player_data
            WHERE player_id = %s""", [playerId])
        return Player.cur.fetchone()

    def getMobileOwnerId(mobile):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_mobile = %s""", [mobile])
        return Player.cur.fetchone()

    def getMobileById(playerId):
        Player.cur.execute("""SELECT player_mobile FROM player_data
            WHERE player_id = %s""", [playerId])
        return Player.cur.fetchone()

    def _generateFleeingCode(playerId):
        Player.cur.execute("""UPDATE player_data
            SET player_fleeing_code = %s
            WHERE player_id = %s""", (random.randint(100,999), playerId))

    def checkFleeingCode(playerId, code):
        return Player.getFleeingCode(playerId) == code

    def getFleeingCode(playerId):
        Player.cur.execute("""SELECT player_fleeing_code FROM player_data
            WHERE player_id = %s""", [playerId])
        return Player.cur.fetchone()

    def getAllPlayerIds():
        Player.cur.execute("""SELECT player_id FROM player_data """)
        return Player.cur.fetchall()


    def print():
        Player.cur.execute("""SELECT * FROM player_data """)
        rows = Player.cur.fetchall()
        print("Players:")
        for player in rows:
            print(" - ", player[1], player[2], player[3])

    def printDetailed():
        Player.cur.execute("""SELECT player_data.player_id, player_data.player_name, player_data.player_mobile, team_players.team_id, player_data.player_fleeing_code, code_list.spot_code, code_list.touch_code
            FROM player_data 
                JOIN code_list ON (player_data.player_code_id = code_list.code_id)
                JOIN team_players ON (player_data.player_id = team_players.player_id)
            """)
        rows = Player.cur.fetchall()
        for row in rows:
            (id, name, mobile, teamId, fleeingCode, spotCode, touchCode) = row
            print(" - ", id, mobile, teamId, fleeingCode, spotCode, touchCode, Event.isPlayerJailed(row[0]), name)
