import psycopg2

class Spawn:

# init
	def initDB(cursor):
		Spawn.cur = cursor
		Spawn._createSpawnmasterData()
		Spawn.addDefaultMaster()

	def initConnect(cursor):
		Spawn.cur = cursor

	def _createSpawnmasterData():
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

	def addDefaultMaster():
		Spawn.cur.execute("""INSERT INTO spawnmasters (master_name, master_pw) 
				VALUES (%s, %s)""", ("spawn", "master"))
