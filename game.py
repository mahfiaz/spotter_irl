import psycopg2
import datetime
import time
import random

dateformat = '%Y-%m-%d %H:%M:%S'


try:
    conn = psycopg2.connect("dbname='sms_game_engine' user='Leevi' host='localhost' password='321'")
except:
    print ("unable to connect to the database")

cur = conn.cursor()


def createRoundDataTable():
    cur.execute("""CREATE TABLE round_data (
        round_id serial PRIMARY KEY,
        round_name VARCHAR(30) NOT NULL,
        round_start TIMESTAMP,
        round_end TIMESTAMP)""")

def createPlayerDataTable():
    cur.execute("""CREATE TABLE player_data (
        player_id serial PRIMARY KEY,
        player_name varchar(128) UNIQUE,
        player_mobile varchar(64) UNIQUE,
        player_email varchar(128) UNIQUE,
        player_shot_id int DEFAULT 0,
        player_headshotcode_id int DEFAULT 0,
        player_created timestamp DEFAULT NOW() )""")

def createTeamTable():
    cur.execute("""CREATE TABLE team (
        team_id serial PRIMARY KEY,
        team_name VARCHAR(30) NOT NULL,
        round_id int)""")

def createTeamPlayersTable():
    cur.execute("""CREATE TABLE team_players (
        player_id int,
        team_id int,
        added timestamp)""")

def createShotCodeTable():
    cur.execute("""CREATE TABLE shot_code (
        shot_id serial PRIMARY KEY,
        shot_value int unique,
        player_id int,
        added timestamp DEFAULT NOW())""")

def findShotCode(code):
    cur.execute("""SELECT shot_id, player_id
        FROM shot_code
        WHERE shot_value = %s""", [code])
    found = cur.fetchone()
    if found:
        return found
    return False

def generateShotCode(player_id):
    fail = True
    new_code = 0
    while fail:
        new_code = random.randint(1000,9999)
        fail = findShotCode(new_code)
    cur.execute("""INSERT INTO shot_code (shot_value, player_id)
        VALUES (%s, %s)""", (new_code, player_id))
    cur.execute("""SELECT shot_id
        FROM shot_code 
        WHERE shot_value = %s""", [new_code])
    id = cur.fetchone()
    cur.execute("""UPDATE player_data
        SET player_shot_id = %s
        WHERE player_id = %s""", (id, player_id))

def findWhoWasShot(code):
    found = findShotCode(code)
    if found:
        shotId, playerId = found
        cur.execute("""UPDATE shot_code
            SET player_id = NULL
            WHERE shot_id = %s""", shotId)
        cur.execute("""UPDATE player_data
            SET player_shot_id = %s
            WHERE player_id = %s""", (shotId, playerId))
        return playerId
    else:
        return False

def addRound(name, time_start, time_end):
    cur.execute("""SELECT round_name
        FROM round_data 
        WHERE (round_start = %s OR (round_start < %s AND round_end > %s)) OR
        (round_end = %s AND (round_start < %s AND round_end > %s))""",
        (time_start, time_start, time_start, time_end, time_end, time_end))
    if not cur.fetchall():
        cur.execute("""INSERT INTO round_data (round_name, round_start, round_end)
            VALUES (%s, %s, %s)""", (name, time_start, time_end))
        return True
    else:
        print("Error: New round has overlapping time. not added", name, time_start, time_end)
        return False


def addRounds():
    time.strftime(dateformat)
    time1 = format(datetime.datetime.now() + datetime.timedelta(hours = -2), dateformat)
    time2 = format(datetime.datetime.now() + datetime.timedelta(hours = -1), dateformat)
    time3 = format(datetime.datetime.now() + datetime.timedelta(hours = 0), dateformat)
    time4 = format(datetime.datetime.now() + datetime.timedelta(hours = 1), dateformat)

    dataDict = ({"name":"eelmine mäng", "time_start":time1, "time_end":time2},
            {"name":"praegune mäng", "time_start":time2, "time_end":time3},
            {"name":"järgmine mäng", "time_start":time3, "time_end":time4})
    addRound("eelmine mäng", time1, time2)
    addRound("praegune mäng", time2, time3)
    addRound("järgmine mäng", time3, time4)
#    addRound("vale mäng", time2, time4)

def getActiveRound():
    cur.execute("""SELECT round_id, round_name 
        FROM round_data 
        WHERE (round_start <= NOW() AND round_end > NOW())""")
    active = cur.fetchone()
    if active:
        id, name = active
        return id
    else:
        return False

def isRoundActive():
    if getActiveRound():
        return True
    else:
        return False

def printRounds():
    cur.execute("""SELECT round_id, round_name, round_start, round_end 
        FROM round_data """)
    rows = cur.fetchall()
    active = getActiveRound()
    print("Rounds:")
    for row in rows:
        id, name, time1, time2 = row
        indicator = " - "
        if id == active:
            indicator = " * "
        print(indicator, id, name, time1, time2)



def addPlayer(name, mobile, email):
    cur.execute("""SELECT (player_name, player_mobile, player_email)
        FROM player_data 
        WHERE player_name = %s OR player_mobile = %s OR player_email = %s""",
        (name, mobile, email))
    rows = cur.fetchall()
    if not rows:
        try:
            cur.execute("""INSERT INTO player_data (player_name, player_mobile, player_email)
                VALUES (%s, %s, %s)""", (name, mobile, email))
            print("Player added.", name, mobile, email)
            return True
        except:
            print("wierd error")
            pass
    else:
        print("not entirely unique player. not added")
    return False


def addPlayers():
    dataDict = ({"name":"Ets2", "mobile":"550054", "email":"ets@gail.cm"},
            {"name":"Vollts", "mobile":"5500547", "email":"Volts@gail.cm"},
            {"name":"KalleLalle", "mobile":"581845", "email":"KAlli@gail.cm"})
    for each in dataDict:
        addPlayer(each['name'], each['mobile'], each['email'])


def printPlayers():
    cur.execute("""SELECT * FROM player_data """)
    rows = cur.fetchall()
    print("Players:")
    for player in rows:
        print(" - ", player[1], player[2], player[3])



def main():
    createRoundDataTable()
    createPlayerDataTable()
    createShotCodeTable()
    addRounds()
    addPlayers()
#    time.sleep(5)
    addPlayer("Vollts2", "3593", "ille2@gmail.ocom")
    printRounds()
    print("round active", isRoundActive())
    printPlayers()


if __name__ == "__main__":
    main()