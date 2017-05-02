import random
import game_config
import math

import psycopg2

from .helper import iterateZero

class Player:

# init
    def initOnce(cursor):
        Player.cur = cursor
        Player._createDataTable()

    def _createDataTable():
        Player.cur.execute("""CREATE TABLE player_data (
            player_id serial PRIMARY KEY,
            player_name varchar(32) UNIQUE,
            player_mobile varchar(16) UNIQUE,
            player_email varchar(64) UNIQUE,
            player_code_id int DEFAULT 0,
            player_fleeing_code int DEFAULT 0,
            player_created timestamp DEFAULT statement_timestamp() )""")

# modify
    def add(name, mobile, email):
        Player.cur.execute("""SELECT player_name, player_mobile, player_email
            FROM player_data 
            WHERE player_name = %s OR player_mobile = %s OR player_email = %s""",
            (name, mobile, email))
        if not Player.cur.fetchone():
            Player.cur.execute("""INSERT INTO player_data (player_name, player_mobile, player_email) VALUES (%s, %s, %s)""", (name, mobile, email))
            newId = Player._getIdByName(name)
            Player._generateFleeingCode(newId)
            return newId

# gets
    def _getIdByName(playerName):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_name = %s""", [playerName])
        return iterateZero(Player.cur.fetchone())

    def getNameById(playerId):
        Player.cur.execute("""SELECT player_name FROM player_data
            WHERE player_id = %s""", (playerId,))
        try:
            name = iterateZero(Player.cur.fetchone())
            return name
        except psycopg2.ProgrammingError:
#TODO solve this bug
            print("ERROR! getNameById error. THIS IS BUGGG", playerId)


    def getMobileOwnerId(mobile):
        Player.cur.execute("""SELECT player_id FROM player_data
            WHERE player_mobile = %s""", [mobile])
        return iterateZero(Player.cur.fetchone())

    def getMobileById(playerId):
        Player.cur.execute("""SELECT player_mobile FROM player_data
            WHERE player_id = %s""", [playerId])
        try:
            mobile = iterateZero(Player.cur.fetchone())
            return mobile
        except psycopg2.ProgrammingError:
#TODO solve this bug
            print("ERROR! getMobile error. THIS IS BUGGG", playerId)

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

# list
    def getAllPlayerIds():
        Player.cur.execute("""SELECT player_id FROM player_data """)
        return Player.cur.fetchall()


    def print():
        Player.cur.execute("""SELECT * FROM player_data """)
        rows = Player.cur.fetchall()
        print("Players:")
        for player in rows:
            print(" - ", player[1], player[2], player[3])
