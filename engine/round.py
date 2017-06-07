import time


class Round:
    id = None
    name = None
    start = None
    end = None

    def __init__(self, parent, id=None, name=None, start=None, end=None):
        self.parent = parent
        self.log = parent.log
        self.cur = parent.cur

        if id:
            self.id = id
            self.load()
        elif name or self.start:
            # Create and save a new round
            self.name = name
            if not self.name:
                self.name = ''
            self.start = start
            self.end = end
            self.save()

    def load(self):
        self.log.debug("Loaded round with id=%d" % self.id)
        self.cur.execute("""SELECT name, round_start, round_end FROM rounds
            WHERE round_id = %s)""", (self.id))
        self.name, self.start, self.end = self.cur.fetchone()

    def save(self):
        self.log.debug("Saved round with id=%d" % self.id)
        self.cur.execute("""UPDATE rounds SET
            name=%s, round_start=%s, round_end=%s WHERE round_id=%s""",
            (self.name, self.start, self.end, self.id))

    # Use if round.active: or set round.active = True or False
    @property
    def active(self):
        if self.start and self.end:
            time = time.now()
            if self.start < time and time < self.end:
                return True
        return False

    @active.setter
    def active(self, value):
        # The round is set active
        pass

    def print():
        print("Round #%d %s, start %s, end %s, color %s" % \
                (self.id, self.name, self.start, self.end))

class Rounds:
    current = None

    def __init__(self, parent):
        self.parent = parent
        self.cur = parent.cur

        self.find_active()

    def find_active(self):
        now = time.time()
        self.cur.execute("""SELECT round_id FROM rounds WHERE
            round_start < statement_timestamp() AND round_end > statement_timestamp()""")
        print(self.cur.fetchone())

    def get_rounds(self):
        self.cur.execute("""SELECT round_id, name, round_start, round_end
            FROM rounds""")
        rows = self.cur.fetchall()
        active = Round.getActiveId()
        #print("Rounds:")
        rounds = []
        for row in rows:
            id, name, time1, time2 = row
            indicator = " - "
            if id == active:
                indicator = " * "
            #print(indicator, id, name, time1, time2)
            round = []
            round.append(indicator)
            round.append(id)
            round.append(name)
            round.append(time1)
            round.append(time2)
            rounds.append(round)
        return rounds

    def next(self):
        self.cur.execute("""SELECT round_start
            FROM rounds
            WHERE (round_start > statement_timestamp())
            ORDER BY round_start ASC""")
        return iterateZero(self.cur.fetchone())

    def init_database(cursor):
        cursor.execute("""DROP TABLE IF EXISTS rounds""")
        cursor.execute("""CREATE TABLE rounds (
            round_id serial PRIMARY KEY,
            name VARCHAR(30) NOT NULL,
            round_start TIMESTAMP,
            round_end TIMESTAMP)""")
