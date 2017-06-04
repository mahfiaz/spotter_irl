import random
import game_config
import math
import hashlib
import psycopg2

from .helper import iterateZero



class PlayerNew:

    def __init__(self, cursor, id):
        self.cur = cursor
        self.id = id

    def __del__(self):
        pass

    def update(self):
        self.cur.execute("SELECT * FROM players WHERE pid = %s", (self.id,))
        data = Player.cur.fetchone()
        self.id, self.name, self.mobile, self.email, self.cid, self.chat_banned, self.fleeing_code, self.web_hash, self.created = data

    def _generate_fleeing_code(self):
        unique = True
        while unique:
            code_max = math.pow(10, game_config.player_fleeingCodeDigits)
            fleeing_code = random.randint(codeMax / 10, codeMax - 1)
            cursor.execute("""SELECT * FROM players
                WHERE fleeing_code = %s""",(fleeing_code,))
            if not cursor.fetchone():
                Player.cur.execute("""UPDATE players
                    SET fleeing_code = %s
                    WHERE pid = %s""", (fleeing_code, self.id))
                self.update()
                return

    def ban_chat(self):
        self.cur.execute("""UPDATE players SET banned = %s
            WHERE pid = %s""", ('true', self.id))
        self.update()

    def unban_chat(self):
        self.cur.execute("""UPDATE players SET banned = %s
            WHERE pid = %s""", ('false', self.id))


class Players:

    def __init__(self, cursor):
        self.cur = cursor
        self.all = []
        for id in data:
            someone = PlayerNew(self.cur, id)
            someone.update()
            self.all.append(someone)

    def add(name, mobile, email):
        self.cur.execute("""SELECT name, mobile, email
            FROM players
            WHERE name = %s OR mobile = %s""",
            (name, mobile))
        if not self.cur.fetchone():
            hash = self._generate_hash(name)
            self.cur.execute("""INSERT INTO players (name, mobile, email, cookie)
                VALUES (%s, %s, %s, %s)""", (name, mobile, email, hash))

            self.cur.execute("""SELECT pid FROM players
                WHERE name = %s""", [name])
            id = iterateZero(self.cur.fetchone())
            newby = PlayerNew(cursor, id)
            newby._generate_fleeing_code()
            self.all.append(newby)
            return newby

    def delete(somebody):
        for someone in self.all:
            if someone == somebody:
                self.all.remove(somebody)
                self.cur.execute("DELETE FROM players WHERE pid = %s",(somebody.id,))
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
            self.cur.execute("""SELECT * FROM players
                WHERE cookie = %s""",(hash,))
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
        Player.cur.execute("""DROP TABLE IF EXISTS players""")
        Player.cur.execute("""CREATE TABLE players (
            pid serial PRIMARY KEY,
            name varchar(32) UNIQUE,
            mobile varchar(16) UNIQUE,
            email varchar(64),
            cid int DEFAULT 0,
            banned boolean DEFAULT false,
            fleeing_code int DEFAULT 0,
            cookie char(6) UNIQUE,
            created timestamp DEFAULT statement_timestamp() )""")


# Delete player, who added wrong data to avoid phonenumber and username conflicts
    def delPlayer(playerName):
        Player.cur.execute("""DELETE FROM players WHERE name = %s""",(playerName,))



# modify
    def add(name, mobile, email):
        Player.cur.execute("""SELECT name, mobile, email
            FROM players
            WHERE name = %s OR mobile = %s""",
            (name, mobile))
        if not Player.cur.fetchone():
            hash = Player._generateHash(name)
            Player.cur.execute("""INSERT INTO players (name, mobile, email, cookie)
                VALUES (%s, %s, %s, %s)""", (name, mobile, email, hash))
            newId = Player._getIdByName(name)
            Player._generateFleeingCode(newId)
            return newId

    def _generateHash(name):
        unique = True
        while unique:
            hash = hashlib.sha224(name.encode('utf-8')).hexdigest()[-6:]
            Player.cur.execute("""SELECT * FROM players
                WHERE name = %s""",(hash,))
            if not Player.cur.fetchone():
                return hash

# gets
    def _getIdByName(playerName):
        Player.cur.execute("""SELECT pid FROM players
            WHERE name = %s""", [playerName])
        return iterateZero(Player.cur.fetchone())

    def getIdByHash(hash):
        Player.cur.execute("""SELECT pid FROM players
            WHERE cookie = %s""", [hash])
        return iterateZero(Player.cur.fetchone())

    def getHashById(playerId):
        Player.cur.execute("""SELECT cookie FROM players
            WHERE pid = %s""", (playerId,))
        return iterateZero(Player.cur.fetchone())

    def getNameById(playerId):
        Player.cur.execute("""SELECT name FROM players
            WHERE pid = %s""", (playerId,))
        return iterateZero(Player.cur.fetchone())

    def getMobileOwnerId(mobile):
        Player.cur.execute("""SELECT pid FROM players
            WHERE mobile = %s""", [mobile])
        return iterateZero(Player.cur.fetchone())

    def getMobileById(playerId):
        Player.cur.execute("""SELECT mobile FROM players
            WHERE pid = %s""", [playerId])
        return iterateZero(Player.cur.fetchone())

    def getMasterId():
        return Player._getIdByName(game_config.master_player['name'])

# flee
    def _generateFleeingCode(playerId):
        codeMax = math.pow(10, game_config.player_fleeingCodeDigits)
        Player.cur.execute("""UPDATE players
            SET fleeing_code = %s
            WHERE pid = %s""", (random.randint(codeMax / 10, codeMax - 1), playerId))

    def checkFleeingCode(code):
        Player.cur.execute("""SELECT pid FROM players
            WHERE fleeing_code = %s""", [code])
        return iterateZero(Player.cur.fetchone())

    def getFleeingCode(playerId):
        Player.cur.execute("""SELECT fleeing_code FROM players
            WHERE pid = %s""", [playerId])
        return iterateZero(Player.cur.fetchone())

# ban chat
    def banChat(playerId):
        Player.cur.execute("""UPDATE players SET banned = %s
            WHERE pid = %s""", ('true', playerId))

    def unbanChat(playerId):
        Player.cur.execute("""UPDATE players SET banned = %s
            WHERE pid = %s""", ('false', playerId))

    def isBannedChat(playerId):
        Player.cur.execute("""SELECT banned FROM players
            WHERE pid = %s""", (playerId,))
        if(Player.cur.fetchone()[0]):
            return True


# list
    def getAllPlayerIds():
        Player.cur.execute("""SELECT pid FROM players """)
        playerIds = Player.cur.fetchall()
        return sum(playerIds, ())

    def getPlayerMobilesNamesList():
        playerList = []
        for id in Player.getAllPlayerIds():
            data = Player.getMobileById(id), Player.getNameById(id)
            playerList.append(data)
        return playerList


    def print():
        Player.cur.execute("""SELECT * FROM players """)
        rows = Player.cur.fetchall()
        print("Players:")
        for player in rows:
            print(" - ", player[1], player[2], player[3])
