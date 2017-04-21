#!/usr/bin/env python3

import psycopg2
import datetime
import time
import random
import game_config

dateformat = '%Y-%m-%d %H:%M:%S'

#def connectDB():
database, host = (game_config.connection_dbname, game_config.connection_host)
user, password = (game_config.connection_user, game_config.connection_password)
connParams = "dbname='" + database + "' user='" + user + "' host='" + host + "' password='" + password + "'"
try:
    connection = psycopg2.connect(connParams)
#    return connection
except:
    print ("Error. Unable to connect to the database. If losing data is acceptable, try running 'python reset_db.py'")
#    return False
cur = connection.cursor()

class Round():

    def initOnce(cursor):
        Round.cur = cursor
        Round.createDataTable()

    def createDataTable():
        Round.cur.execute("""CREATE TABLE round_data (
            round_id serial PRIMARY KEY,
            round_name VARCHAR(30) NOT NULL,
            round_start TIMESTAMP,
            round_end TIMESTAMP)""")

    def add(name, time_start, time_end):
        Round.cur.execute("""SELECT round_name
            FROM round_data 
            WHERE (round_start = %s OR (round_start < %s AND round_end > %s)) OR
            (round_end = %s AND (round_start < %s AND round_end > %s))""",
            (time_start, time_start, time_start, time_end, time_end, time_end))
        if not Round.cur.fetchall():
            Round.cur.execute("""INSERT INTO round_data (round_name, round_start, round_end)
                VALUES (%s, %s, %s)""", (name, time_start, time_end))
            return True
        else:
            print("Error: New round has overlapping time. not added", name, time_start, time_end)
            return False

    def getActive():
        Round.cur.execute("""SELECT round_id, round_name
            FROM round_data 
            WHERE (round_start <= NOW() AND round_end > NOW())""")
        active = Round.cur.fetchone()
        if active:
            id, name = active
            return id
        else:
            return False

    def isActive():
        if Round.getActive():
            return True
        else:
            return False

    def print():
        Round.cur.execute("""SELECT round_id, round_name, round_start, round_end
            FROM round_data """)
        rows = Round.cur.fetchall()
        active = Round.getActive()
        print("Rounds:")
        for row in rows:
            id, name, time1, time2 = row
            indicator = " - "
            if id == active:
                indicator = " * "
            print(indicator, id, name, time1, time2)

    def addTestRounds():
        time.strftime(dateformat)
        time1 = format(datetime.datetime.now() + datetime.timedelta(hours = -2), dateformat)
        time2 = format(datetime.datetime.now() + datetime.timedelta(hours = -1), dateformat)
        time3 = format(datetime.datetime.now() + datetime.timedelta(hours = 0), dateformat)
        time4 = format(datetime.datetime.now() + datetime.timedelta(hours = 1), dateformat)

        dataDict = ({"name":"eelmine mäng", "time_start":time1, "time_end":time2},
                {"name":"praegune mäng", "time_start":time2, "time_end":time3},
                {"name":"järgmine mäng", "time_start":time3, "time_end":time4})
        Round.add("eelmine mäng", time1, time2)
        Round.add("praegune mäng", time2, time3)
        Round.add("järgmine mäng", time3, time4)
        Round.add("vale mäng", time2, time4)




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
            player_created timestamp DEFAULT NOW() )""")

    def add(name, mobile, email):
        Player.cur.execute("""SELECT (player_name, player_mobile, player_email)
            FROM player_data 
            WHERE player_name = %s OR player_mobile = %s OR player_email = %s""",
            (name, mobile, email))
        rows = Player.cur.fetchall()
        if not rows:
            Player.cur.execute("""INSERT INTO player_data (player_name, player_mobile, player_email) VALUES (%s, %s, %s)""", (name, mobile, email))
            print("Player added.", name, mobile, email)
            return True
        else:
            print("not entirely unique player. not added")
        return False

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

class Team:

    def initOnce(cursor):
        Team.cur = cursor
        Team.createTeamTable()
        Team.createTeamPlayersTable()

    def createTeamTable():
        Team.cur.execute("""CREATE TABLE team (
            team_id serial PRIMARY KEY,
            team_name VARCHAR(30) NOT NULL,
            round_id int)""")

    def createTeamPlayersTable():
        Team.cur.execute("""CREATE TABLE team_players (
            player_id int,
            team_id int,
            added timestamp)""")



class Code:

    def initOnce(cursor):
        Code.cur = cursor
        Code.createDataTable()

    def createDataTable():
        Code.cur.execute("""CREATE TABLE shot_code (
            shot_id serial PRIMARY KEY,
            shot_value int unique,
            player_id int,
            added timestamp DEFAULT NOW())""")

    def findShotCode(code):
        Code.cur.execute("""SELECT shot_id, player_id
            FROM shot_code
            WHERE shot_value = %s""", [code])
        found = Code.cur.fetchone()
        if found:
            return found
        return False

    def generateShotCode(playerId):
        fail = True
        newCode = 0
        while fail:
            new_code = random.randint(1000,9999)
            fail = Code.findShotCode(newCode)
        Code.cur.execute("""INSERT INTO shot_code (shot_value, player_id)
            VALUES (%s, %s)""", (newCode, playerId))
        Code.cur.execute("""SELECT shot_id
            FROM shot_code 
            WHERE shot_value = %s""", [new_code])
        id = cur.fetchone()
        Code.cur.execute("""UPDATE player_data
            SET player_shot_id = %s
            WHERE player_id = %s""", (id, playerId))

    def findWhoWasShot(code):
        found = Code.findShotCode(code)
        if found:
            shotId, playerId = found
            Code.cur.execute("""UPDATE shot_code
                SET player_id = NULL
                WHERE shot_id = %s""", shotId)
            Code.cur.execute("""UPDATE player_data
                SET player_shot_id = %s
                WHERE player_id = %s""", (shotId, playerId))
            return playerId
        else:
            return False






def main():
#    connection = connectDB()
#    if not connection:
#        return
#    cursor = connection.cursor()
    cursor = cur

    Round.initOnce(cursor)
    Player.initOnce(cursor)
    Code.initOnce(cursor)

    Round.addTestRounds()
    Player.addTestPlayers()
    Player.add("Vollts2", "3593", "ille2@gmail.ocom")

    Round.print()
    print("round active", Round.isActive())
    Player.print()


if __name__ == "__main__":
    main()