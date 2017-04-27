import time
import datetime
import game_config

dateformat = game_config.database_dateformat

class Round():
    _activeId = 0

    def initOnce(cursor):
        Round.cur = cursor
        Round._createDataTable()

    def _createDataTable():
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

    def updateActiveId():
        Round.cur.execute("""SELECT round_id
            FROM round_data 
            WHERE (round_start <= statement_timestamp() AND round_end > statement_timestamp())""")
        Round._activeId = Round.cur.fetchone()
        return Round._activeId

    def getActiveId():
        return Round._activeId

    def isActive():
        if Round.getActiveId():
            return True
        else:
            return False

    def print():
        Round.cur.execute("""SELECT round_id, round_name, round_start, round_end
            FROM round_data """)
        rows = Round.cur.fetchall()
        active = Round.getActiveId()
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

