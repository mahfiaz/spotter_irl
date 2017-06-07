import random
import game_config
import math
import hashlib
import psycopg2


class Player:
    NEW = 0
    SPAWNED = 1
    KILLED = 2
    # State NEW
    state = 0

    # Database cursor
    cur = None
    updated = False

    # Main data
    id = None
    name = ''
    mobile = ''
    banned = None

    # Other
    team = None
    codes = None
    cookie = None

    def __init__(self, parent, pid=None, name=None, mobile=None):
        self.parent = parent
        self.log = parent.log
        self.cur = parent.cur

        if pid:
            self.log.info("Loading player with id=%d" % pid)
            self.id = pid
            self.load()
        else:
            self.log.info("Creating new player with name=%s, mobile=%s" % (name, mobile))
            self.create(name, mobile)
            print("Created")

    def create(self, name, mobile):
        self.name = name
        self.mobile = mobile
        self.cookie = self.generate_hash(name)
        try:
            self.cur.execute("""INSERT INTO player
                (name, mobile, cookie)
                VALUES (%s, %s, %s) RETURNING pid""",
                (name, mobile, self.cookie))
            result = self.cur.fetchone()
            self.id = result[0]
        except psycopg2.IntegrityError:
            self.log.warning("User already exists name=%s mobile=%s", name, mobile)
            pass
        self.log.info("Added user %s" % self)

    def load(self):
        self.cur.execute("SELECT * FROM player WHERE pid = %s", (self.id,))
        data = self.cur.fetchone()
        if data:
            self.id, self.name, self.mobile, self.email, self.cid, self.chat_banned, self.web_hash, self.created = data

    def save(self):
        self.cur.execute("UPDATE player SET WHERE pid = %s", (self.id,))
        data = Player.cur.fetchone()
        self.id, self.name, self.mobile, self.email, self.cid, self.chat_banned, self.web_hash, self.created = data

    def ban(self, now = False):
        self.cur.execute("""UPDATE player SET banned = %s
            WHERE pid = %s""", ('true', self.id))
        self.update()
        if now:
            self.save()

    def unban(self, now = False):
        self.cur.execute("""UPDATE player SET banned = %s
            WHERE pid = %s""", ('false', self.id))
        if now:
            self.save()

    def delete(self):
        self.log.info("Deleted %s" % self)
        self.cur.execute("""DELETE FROM player WHERE pid = %s""", (self.id,))
        self.cur.execute("""DELETE FROM team_players
            WHERE pid = %s""", (self.id,))
        # TODO also delete from every other table
        del self

    def generate_hash(self, name):
        hash_ = hashlib.sha224(name.encode('utf-8')).hexdigest()[-6:]
        return hash_

    def __str__(self):
        """ Makes printing object easy """
        return "<Player #%s, name=%s, mobile=%s, banned=%s>" % \
            (self.id, self.name, self.mobile, self.banned)


class Players:
    def __init__(self, parent):
        self.parent = parent
        self.cur = parent.cur
        self.log = parent.log

        self.all = []
        self.load_all()

    def add(self, name, mobile):
        self.log.info("Adding player with name=%s, mobile=%s", name, mobile)
        player = Player(self.parent, name=name, mobile=mobile)
        self.all.append(player)
        return player

    def find(self, name=None, mobile=None, cookie=None, code=None):
        if name:
            for someone in self.all:
                if someone.name == name:
                    return someone
                else:
                    self.cur.execute("""SELECT pid FROM player
                        WHERE name = %s""", (name,))
                    return iterateZero(self.cur.fetchone())
        elif mobile:
            for someone in self.all:
                if someone.mobile == mobile:
                    return someone
                else:
                    self.cur.execute("""SELECT pid FROM player
                        WHERE mobile = %s""", (mobile,))
                    self.pid = self.cur.fetchone()[0]
                    return iterateZero(self.cur.fetchone())
        elif cookie:
            for someone in self.all:
                if someone.hash == hash:
                    return someone
                else:
                    Player.cur.execute("""SELECT pid FROM player
                        WHERE cookie = %s""", (hash,))
                    return iterateZero(Player.cur.fetchone())
        elif code:
            for someone in self.all:
                if someone.fleeing_code == code:
                    return someone

    def load_all(self):
        self.cur.execute("""SELECT pid FROM player ORDER BY pid""")
        for pid in self.cur.fetchall():
            self.all.append(Player(self.parent, pid=pid))

    def print_all(self):
        for player in self.all:
            print(player)

    def init_database(cursor):
        cursor.execute("""DROP TABLE IF EXISTS player""")
        cursor.execute("""CREATE TABLE player (
            pid serial PRIMARY KEY,
            name varchar(32) UNIQUE,
            mobile varchar(16) UNIQUE,
            email varchar(64),
            code_id int DEFAULT 0,
            banned boolean DEFAULT false,
            cookie char(6) UNIQUE,
            created timestamp DEFAULT statement_timestamp())""")
