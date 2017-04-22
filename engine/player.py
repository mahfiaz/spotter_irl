import random

class Player:

    def initOnce(cursor):
        Player.cur = cursor
        Player.createDataTable()

    def createDataTable():
        Player.cur.execute("""CREATE TABLE player_data (
            player_id serial PRIMARY KEY,
            player_name varchar(128) UNIQUE,
            player_mobile varchar(64) UNIQUE,
            player_email varchar(128) UNIQUE,
            player_shot_id int DEFAULT 0,
            player_headshotcode_id int DEFAULT 0,
            player_respawn_code int DEFAULT 0,
            player_created timestamp DEFAULT statement_timestamp() )""")

    def add(name, mobile, email):
        Player.cur.execute("""SELECT (player_name, player_mobile, player_email)
            FROM player_data 
            WHERE player_name = %s OR player_mobile = %s OR player_email = %s""",
            (name, mobile, email))
        rows = Player.cur.fetchall()
        if not rows:
            Player.cur.execute("""INSERT INTO player_data (player_name, player_mobile, player_email) VALUES (%s, %s, %s)""", (name, mobile, email))
            print("Player added.", name, mobile, email)
            return Player.getIdByName(name)
        else:
            print("not entirely unique player. not added")
        return False

    def getIdByName(playerName):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_name = %s""", [playerName])
        return Player.cur.fetchone()

    def getIdByMobile(mobile):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_mobile = %s""", [mobile])
        return Player.cur.fetchone()

    def getMobileById(playerId):
        Player.cur.execute("""SELECT player_mobile FROM player_data
            WHERE player_id = %s""", [playerId])
        return Player.cur.fetchone()

    def getNameById(playerId):
        Player.cur.execute("""SELECT player_name FROM player_data
            WHERE player_id = %s""", [playerId])
        return Player.cur.fetchone()



    def regenerateRespawnCode(playerId):
        Player.cur.execute("""UPDATE player_data
            SET player_respawn_code = %s
            WHERE player_id = %s""", (random.randint(100,999), playerId))

    def checkRespawnCode(playerId, code):
        Player.cur.execute("""SELECT player_respawn_code FROM player_data
            WHERE player_id = %s""", [playerId])
        return Player.cur.fetchone() == code



    def print():
        Player.cur.execute("""SELECT * FROM player_data """)
        rows = Player.cur.fetchall()
        print("Players:")
        for player in rows:
            print(" - ", player[1], player[2], player[3])

    def addTestPlayers():
        dataDict = ({"name":"Ets2", "mobile":"550054", "email":"ets@gail.cm"},
                {"name":"Vollts", "mobile":"5500547", "email":"Volts@gail.cm"},
                {"name":"KalleLalle", "mobile":"581845", "email":"KAlli@gail.cm"})
        for each in dataDict:
            Player.add(each['name'], each['mobile'], each['email'])
