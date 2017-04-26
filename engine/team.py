#import player
from .player import Player

class Team:

    def initOnce(cursor):
        Team.cur = cursor
        Team._createTeamTable()
        Team._createTeamPlayersTable()

    def _createTeamTable():
        Team.cur.execute("""CREATE TABLE team_list (
            team_id serial PRIMARY KEY,
            team_name VARCHAR(30) NOT NULL,
            round_id int)""")

    def _createTeamPlayersTable():
        Team.cur.execute("""CREATE TABLE team_players (
            player_id int,
            team_id int,
            added timestamp DEFAULT statement_timestamp() )""")

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
        Team.cur.execute("""SELECT team_players.team_id, player_data.player_id, player_data.player_name
            FROM team_players JOIN player_data ON (team_players.player_id = player_data.player_id)
            WHERE team_players.team_id IN
            (SELECT team_id FROM team_list)""")
        teams = Team.cur.fetchall()
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
        Team.addPlayer(1, Team.getIdByName('Sinised'))
        Team.addPlayer(2, Team.getIdByName('Sinised'))
        Team.addPlayer(3, Team.getIdByName('Punased'))
        Team.addPlayer(4, Team.getIdByName('Punased'))
