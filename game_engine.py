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

    firstRun = True

    def __init__(self, cursor):
        self.cur = cursor
        if Round.firstRun:
            self.createDataTable()
            Round.firstRun = False

    def createDataTable(self):
        self.cur.execute("""CREATE TABLE round_data (
            round_id serial PRIMARY KEY,
            round_name VARCHAR(30) NOT NULL,
            round_start TIMESTAMP,
            round_end TIMESTAMP)""")

    def add(self, name, time_start, time_end):
        self.cur.execute("""SELECT round_name
            FROM round_data 
            WHERE (round_start = %s OR (round_start < %s AND round_end > %s)) OR
            (round_end = %s AND (round_start < %s AND round_end > %s))""",
            (time_start, time_start, time_start, time_end, time_end, time_end))
        if not self.cur.fetchall():
            self.cur.execute("""INSERT INTO round_data (round_name, round_start, round_end)
                VALUES (%s, %s, %s)""", (name, time_start, time_end))
            return True
        else:
            print("Error: New round has overlapping time. not added", name, time_start, time_end)
            return False

    def getActive(self):
        self.cur.execute("""SELECT round_id, round_name
            FROM round_data 
            WHERE (round_start <= NOW() AND round_end > NOW())""")
        active = self.cur.fetchone()
        if active:
            id, name = active
            return id
        else:
            return False

    def isActive(self):
        if self.getActive():
            return True
        else:
            return False

    def print(self):
        self.cur.execute("""SELECT round_id, round_name, round_start, round_end
            FROM round_data """)
        rows = self.cur.fetchall()
        active = self.getActive()
        print("Rounds:")
        for row in rows:
            id, name, time1, time2 = row
            indicator = " - "
            if id == active:
                indicator = " * "
            print(indicator, id, name, time1, time2)

    def addTestRounds(self):
        time.strftime(dateformat)
        time1 = format(datetime.datetime.now() + datetime.timedelta(hours = -2), dateformat)
        time2 = format(datetime.datetime.now() + datetime.timedelta(hours = -1), dateformat)
        time3 = format(datetime.datetime.now() + datetime.timedelta(hours = 0), dateformat)
        time4 = format(datetime.datetime.now() + datetime.timedelta(hours = 1), dateformat)

        dataDict = ({"name":"eelmine mäng", "time_start":time1, "time_end":time2},
                {"name":"praegune mäng", "time_start":time2, "time_end":time3},
                {"name":"järgmine mäng", "time_start":time3, "time_end":time4})
        self.add("eelmine mäng", time1, time2)
        self.add("praegune mäng", time2, time3)
        self.add("järgmine mäng", time3, time4)
        self.add("vale mäng", time2, time4)




class Player:

    firstRun = True

    def __init__(self, cursor):
        self.cur = cursor
        if Player.firstRun:
            self.createDataTable()
            Player.firstRun = False

    def createDataTable(self):
        self.cur.execute("""CREATE TABLE player_data (
            player_id serial PRIMARY KEY,
            player_name varchar(128) UNIQUE,
            player_mobile varchar(64) UNIQUE,
            player_email varchar(128) UNIQUE,
            player_shot_id int DEFAULT 0,
            player_headshotcode_id int DEFAULT 0,
            player_created timestamp DEFAULT NOW() )""")

    def add(self, name, mobile, email):
        self.cur.execute("""SELECT (player_name, player_mobile, player_email)
            FROM player_data 
            WHERE player_name = %s OR player_mobile = %s OR player_email = %s""",
            (name, mobile, email))
        rows = self.cur.fetchall()
        if not rows:
            self.cur.execute("""INSERT INTO player_data (player_name, player_mobile, player_email) VALUES (%s, %s, %s)""", (name, mobile, email))
            print("Player added.", name, mobile, email)
            return True
        else:
            print("not entirely unique player. not added")
        return False

    def print(self):
        self.cur.execute("""SELECT * FROM player_data """)
        rows = self.cur.fetchall()
        print("Players:")
        for player in rows:
            print(" - ", player[1], player[2], player[3])

    def addTestPlayers(self):
        dataDict = ({"name":"Ets2", "mobile":"550054", "email":"ets@gail.cm"},
                {"name":"Vollts", "mobile":"5500547", "email":"Volts@gail.cm"},
                {"name":"KalleLalle", "mobile":"581845", "email":"KAlli@gail.cm"})
        for each in dataDict:
            self.add(each['name'], each['mobile'], each['email'])

class Team:

    firstRun = True

    def __init__(self, cursor):
        self.cur = cursor
        if Team.firstRun:
            self.createTeamTable()
            self.createTeamPlayersTable()
            Team.firstRun = False
            
    def createTeamTable(self):
        self.cur.execute("""CREATE TABLE team (
            team_id serial PRIMARY KEY,
            team_name VARCHAR(30) NOT NULL,
            round_id int)""")

    def createTeamPlayersTable(self):
        self.cur.execute("""CREATE TABLE team_players (
            player_id int,
            team_id int,
            added timestamp)""")



class Code:

    firstRun = True

    def __init__(self, cursor):
        self.cur = cursor
        if Code.firstRun:
            self.createDataTable()
            Code.firstRun = False

    def createDataTable(self):
        self.cur.execute("""CREATE TABLE shot_code (
            shot_id serial PRIMARY KEY,
            shot_value int unique,
            player_id int,
            added timestamp DEFAULT NOW())""")

    def findShotCode(self, code):
        self.cur.execute("""SELECT shot_id, player_id
            FROM shot_code
            WHERE shot_value = %s""", [code])
        found = self.cur.fetchone()
        if found:
            return found
        return False

    def generateShotCode(self, playerId):
        fail = True
        newCode = 0
        while fail:
            new_code = random.randint(1000,9999)
            fail = self.findShotCode(newCode)
        self.cur.execute("""INSERT INTO shot_code (shot_value, player_id)
            VALUES (%s, %s)""", (newCode, playerId))
        self.cur.execute("""SELECT shot_id
            FROM shot_code 
            WHERE shot_value = %s""", [new_code])
        id = cur.fetchone()
        self.cur.execute("""UPDATE player_data
            SET player_shot_id = %s
            WHERE player_id = %s""", (id, playerId))

    def findWhoWasShot(self, code):
        found = self.findShotCode(code)
        if found:
            shotId, playerId = found
            self.cur.execute("""UPDATE shot_code
                SET player_id = NULL
                WHERE shot_id = %s""", shotId)
            self.cur.execute("""UPDATE player_data
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

    round = Round(cursor)
    player = Player(cursor)
    code = Code(cursor)

    round.addTestRounds()
    player.addTestPlayers()
    player.add("Vollts2", "3593", "ille2@gmail.ocom")

    round.print()
    print("round active", round.isActive())
    player.print()


if __name__ == "__main__":
    main()