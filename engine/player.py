import random
import game_config
import math
import hashlib
import psycopg2

from .helper import iterateZero

a =

class PlayerNew:

    def __init__(self, cursor, id):
        self.cur = cursor
        self.id = id

    def __del__(self):
        pass

    def update(self):
        self.cur.execute("SELECT * FROM player_data WHERE player_id = %s", (self.id,))
        data = Player.cur.fetchone()
        self.id, self.name, self.mobile, self.email, self.code_id, self.chat_banned, self.fleeing_code, self.web_hash, self.created = data

    def _generate_fleeing_code(self):
        unique = True
        while unique:
            code_max = math.pow(10, game_config.player_fleeingCodeDigits)
            fleeing_code = random.randint(codeMax / 10, codeMax - 1)
            cursor.execute("""SELECT * FROM player_data
                WHERE player_fleeing_code = %s""",(fleeing_code,))
            if not cursor.fetchone():
                Player.cur.execute("""UPDATE player_data
                    SET player_fleeing_code = %s
                    WHERE player_id = %s""", fleeing_code, self.id))
                self.update()
                return

    def ban_chat(self):
        self.cur.execute("""UPDATE player_data SET player_chat_banned = %s
            WHERE player_id = %s""", ('true', self.id))
        self.update()

    def unban_chat(self):
        self.cur.execute("""UPDATE player_data SET player_chat_banned = %s
            WHERE player_id = %s""", ('false', self.id))


class Players:

    def __init__(self, cursor):
        self.cur = cursor
        self.cur.execute("SELECT player_id ORDER BY player_id")
        data = Player.cur.fetchall()
        if len(data) == 0:

        self.all = []
        for id in data:
            someone = PlayerNew(self.cur, id)
            someone.update()
            self.all.append(someone)

    def add(name, mobile, email):
        self.cur.execute("""SELECT player_name, player_mobile, player_email
            FROM player_data
            WHERE player_name = %s OR player_mobile = %s""",
            (name, mobile))
        if not self.cur.fetchone():
            hash = self._generate_hash(name)
            self.cur.execute("""INSERT INTO player_data (player_name, player_mobile, player_email, player_web_hash)
                VALUES (%s, %s, %s, %s)""", (name, mobile, email, hash))

            self.cur.execute("""SELECT player_id FROM player_data
                WHERE player_name = %s""", [name])
            id = iterateZero(self.cur.fetchone())
            newby = PlayerNew(cursor, id)
            newby._generate_fleeing_code()
            self.all.append(newby)
            return newby

    def delete(somebody):
        for someone in self.all:
            if someone == somebody:
                self.all.remove(somebody)
                self.cur.execute("DELETE FROM player_data WHERE player_id = %s",(somebody.id,))
                somebody.__del__()

    def by_name(self, name):
        for someone in self.all:
            if someone.name == name:
                return someone

    def by_mobile(self, mobile):
        for someone in self.all:
            if someone.mobile == mobile:
                return someone

    def by_hash(self, hash):
        for someone in self.all:
            if someone.hash == hash:
                return someone

    def by_fleeing_code(self, code):
        for someone in self.all:
            if someone.fleeing_code == code:
                return someone

    def _generate_hash(self, name):
        unique = True
        while unique:
            hash = hashlib.sha224(name.encode('utf-8')).hexdigest()[-6:]
            self.cur.execute("""SELECT * FROM player_data
                WHERE player_web_hash = %s""",(hash,))
            if not self.cur.fetchone():
                return hash





class Player:

# init
    def initDB(cursor):
        Player.cur = cursor
        Player._createDataTable()

    def initConnect(cursor):
        Player.cur = cursor

    def _createDataTable():
        Player.cur.execute("""DROP TABLE IF EXISTS player_data""")
        Player.cur.execute("""CREATE TABLE player_data (
            player_id serial PRIMARY KEY,
            player_name varchar(32) UNIQUE,
            player_mobile varchar(16) UNIQUE,
            player_email varchar(64),
            player_code_id int DEFAULT 0,
            player_chat_banned boolean DEFAULT false,
            player_fleeing_code int DEFAULT 0,
            player_web_hash char(6) UNIQUE,
            player_created timestamp DEFAULT statement_timestamp() )""")


# Delete player, who added wrong data to avoid phonenumber and username conflicts
    def delPlayer(playerName):
        Player.cur.execute("""DELETE FROM player_data WHERE player_name = %s""",(playerName,))



# modify
    def add(name, mobile, email):
        Player.cur.execute("""SELECT player_name, player_mobile, player_email
            FROM player_data
            WHERE player_name = %s OR player_mobile = %s""",
            (name, mobile))
        if not Player.cur.fetchone():
            hash = Player._generateHash(name)
            Player.cur.execute("""INSERT INTO player_data (player_name, player_mobile, player_email, player_web_hash)
                VALUES (%s, %s, %s, %s)""", (name, mobile, email, hash))
            newId = Player._getIdByName(name)
            Player._generateFleeingCode(newId)
            return newId

    def _generateHash(name):
        unique = True
        while unique:
            hash = hashlib.sha224(name.encode('utf-8')).hexdigest()[-6:]
            Player.cur.execute("""SELECT * FROM player_data
                WHERE player_web_hash = %s""",(hash,))
            if not Player.cur.fetchone():
                return hash

# gets
    def _getIdByName(playerName):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_name = %s""", [playerName])
        return iterateZero(Player.cur.fetchone())

    def getIdByHash(hash):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_web_hash = %s""", [hash])
        return iterateZero(Player.cur.fetchone())

    def getHashById(playerId):
        Player.cur.execute("""SELECT player_web_hash FROM player_data
            WHERE player_id = %s""", (playerId,))
        return iterateZero(Player.cur.fetchone())

    def getNameById(playerId):
        Player.cur.execute("""SELECT player_name FROM player_data
            WHERE player_id = %s""", (playerId,))
        return iterateZero(Player.cur.fetchone())

    def getMobileOwnerId(mobile):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_mobile = %s""", [mobile])
        return iterateZero(Player.cur.fetchone())

    def getMobileById(playerId):
        Player.cur.execute("""SELECT player_mobile FROM player_data
            WHERE player_id = %s""", [playerId])
        return iterateZero(Player.cur.fetchone())

    def getMasterId():
        return Player._getIdByName(game_config.master_player['name'])

# flee
    def _generateFleeingCode(playerId):
        codeMax = math.pow(10, game_config.player_fleeingCodeDigits)
        Player.cur.execute("""UPDATE player_data
            SET player_fleeing_code = %s
            WHERE player_id = %s""", (random.randint(codeMax / 10, codeMax - 1), playerId))

    def checkFleeingCode(code):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_fleeing_code = %s""", [code])
        return iterateZero(Player.cur.fetchone())

    def getFleeingCode(playerId):
        Player.cur.execute("""SELECT player_fleeing_code FROM player_data
            WHERE player_id = %s""", [playerId])
        return iterateZero(Player.cur.fetchone())

# ban chat
    def banChat(playerId):
        Player.cur.execute("""UPDATE player_data SET player_chat_banned = %s
            WHERE player_id = %s""", ('true', playerId))

    def unbanChat(playerId):
        Player.cur.execute("""UPDATE player_data SET player_chat_banned = %s
            WHERE player_id = %s""", ('false', playerId))

    def isBannedChat(playerId):
        Player.cur.execute("""SELECT player_chat_banned FROM player_data
            WHERE player_id = %s""", (playerId,))
        if(Player.cur.fetchone()[0]):
            return True


# list
    def getAllPlayerIds():
        Player.cur.execute("""SELECT player_id FROM player_data """)
        playerIds = Player.cur.fetchall()
        return sum(playerIds, ())

    def getPlayerMobilesNamesList():
        playerList = []
        for id in Player.getAllPlayerIds():
            data = Player.getMobileById(id), Player.getNameById(id)
            playerList.append(data)
        return playerList


    def print():
        Player.cur.execute("""SELECT * FROM player_data """)
        rows = Player.cur.fetchall()
        print("Players:")
        for player in rows:
            print(" - ", player[1], player[2], player[3])
