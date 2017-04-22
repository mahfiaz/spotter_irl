#import player
from .player import Player

class Team:

    def initOnce(cursor):
        Team.cur = cursor
        Team.createTeamTable()
        Team.createTeamPlayersTable()

    def createTeamTable():
        Team.cur.execute("""CREATE TABLE team_list (
            team_id serial PRIMARY KEY,
            team_name VARCHAR(30) NOT NULL,
            round_id int)""")

    def createTeamPlayersTable():
        Team.cur.execute("""CREATE TABLE team_players (
            player_id int,
            team_id int,
            added timestamp DEFAULT NOW() )""")

    def add(teamName):
        teamId = Team.getIdByName(teamName)
        if not teamId:
            Team.cur.execute("""INSERT INTO team_list (team_name)
                VALUES (%s)""", [teamName])
            print("Team ", teamName, " added.")
            return Team.getIdByName(teamName)
        else:
            print("Warning! Team ", teamName, " already exists.")
            return False

    def getIdByName(teamName):
        Team.cur.execute("""SELECT team_id
            FROM team_list
            WHERE team_name = %s""", [teamName])
        return Team.cur.fetchone()

    def getNameById(teamId):
        Team.cur.execute("""SELECT team_name
            FROM team_list
            WHERE team_id = %s""", [teamId])
        return Team.cur.fetchone()

    def getTeamsList():
        Team.cur.execute("""SELECT (team_players.team_id, player_data.player_id, player_data.player_name)
            FROM team_players JOIN player_data ON (team_players.player_id = player_data.player_id)
            WHERE team_players.team_id IN
            (SELECT team_id FROM team_list)""")
        teams = Team.cur.fetchall()
        print(teams)
        return teams

    def getStats():
        pass

    def updateStats():
        pass

    def getPlayerTeamId(playerId):
        Team.cur.execute("""SELECT team_id 
            FROM team_players 
            WHERE player_id = %s""", [playerId])
        return Team.cur.fetchone()

    def removePlayer(playerId):
        if Team.getPlayerTeamId(playerId):
            Team.cur.execute("""DELETE FROM team_players
                WHERE player_id = %s""", [playerId])

    def addPlayer(playerId, teamId):
        Team.removePlayer(playerId)
        Team.cur.execute("""INSERT INTO team_players (player_id, team_id)
            VALUES (%s, %s)""", (playerId, teamId))
        print("Player ", Player.getNameById(playerId), " added to ", Team.getNameById(teamId))

    def addTestTeams():
        Team.add("Sinised")
        Team.add("Punased")
        Team.add("Sinised")

    def addPlayersToTeams():
        Team.addPlayer(Player.getIdByName('Ets2'), Team.getIdByName('Sinised'))
        Team.addPlayer(Player.getIdByName('Vollts'), Team.getIdByName('Sinised'))
        Team.addPlayer(Player.getIdByName('KalleLalle'), Team.getIdByName('Punased'))
        Team.addPlayer(Player.getIdByName('Vollts2'), Team.getIdByName('Punased'))
