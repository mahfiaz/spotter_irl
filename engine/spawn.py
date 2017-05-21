import psycopg2

class Spawn:

# init
	def initDB(cursor):
		Spawn.cur = cursor
		Spawn._create_spawnmaster_data()
		Spawn.add_default_master()

	def initConnect(cursor):
		Spawn.cur = cursor

	def _create_spawnmaster_data():
		Spawn.cur.execute("""DROP TABLE IF EXISTS spawnmasters""")
		Spawn.cur.execute("""CREATE TABLE spawnmasters (
		master_id serial PRIMARY KEY,
			master_name varchar(32) UNIQUE,
			master_pw varchar(16) UNIQUE,
			player_created timestamp DEFAULT statement_timestamp() )""")

	def login():
		master = {}
		Spawn.cur.execute("""SELECT master_name FROM spawnmasters""")
		master["name"] = Spawn.cur.fetchone()
		Spawn.cur.execute("""SELECT master_pw FROM spawnmasters""")
		master["pw"] = Spawn.cur.fetchone()
		return master

	def add_default_master():
		Spawn.cur.execute("""INSERT INTO spawnmasters (master_name, master_pw) 
				VALUES (%s, %s)""", ("spawn", "master"))


class Base:

# init
	def initDB(cursor):
		Base.cur = cursor
		Base._create_basemaster_data()
		Base.add_default_base()

	def initConnect(cursor):
		Base.cur = cursor

	def _create_basemaster_data():
		Base.cur.execute("""DROP TABLE IF EXISTS basemasters""")
		Base.cur.execute("""CREATE TABLE basemasters (
		base_id serial PRIMARY KEY,
			base_name varchar(32) UNIQUE,
			base_pw varchar(16) UNIQUE,
			player_created timestamp DEFAULT statement_timestamp() )""")

	def login():
		master = {}
		Base.cur.execute("""SELECT base_name FROM basemasters""")
		master["name"] = Base.cur.fetchone()
		Base.cur.execute("""SELECT base_pw FROM basemasters""")
		master["pw"] = Base.cur.fetchone()
		return master

	def add_default_base():
		Base.cur.execute("""INSERT INTO basemasters (base_name, base_pw) 
				VALUES (%s, %s)""", ("base", "master"))

