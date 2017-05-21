#import player
from .player import Player
from .round import Round
from .helper import iterateZero

class Team:
    def initDB(cursor):
        Team.cur = cursor
        Team._createTeamTable()
        Team._createTeamPlayersTable()

    def initConnect(cursor):
        Team.cur = cursor

    def _createTeamTable():
        Team.cur.execute("""DROP TABLE IF EXISTS team_list""")
        Team.cur.execute("""CREATE TABLE team_list (
            team_id serial PRIMARY KEY,
            team_name VARCHAR(30) NOT NULL,
            team_color CHAR(6),
            round_id int)""")

    def _createTeamPlayersTable():
        Team.cur.execute("""DROP TABLE IF EXISTS team_players""")
        Team.cur.execute("""CREATE TABLE team_players (
            player_id int,
            team_id int,
            added timestamp DEFAULT statement_timestamp() )""")

# modify teams
    def add(teamName, color, roundId):
        if not Round.existingId(roundId):
            print("Warning. Team", teamName, "not added, because roundId", roundId, "doesn't exist.")
            return
        if not Team._getIdByName(teamName, roundId):
            Team.cur.execute("""INSERT INTO team_list (team_name, round_id, team_color)
                VALUES (%s, %s, %s)""", (teamName, roundId, color))
            print("Team", teamName, "added to round", Round.getName(roundId))
            return Team._getIdByName(teamName, roundId)
        else:
            print("Warning! Team", teamName, "not added, it already exists.")

    def addPlayer(playerId, teamId):
        if not Team.removePlayer(playerId, teamId):
            return
        Team.cur.execute("""INSERT INTO team_players (player_id, team_id)
            VALUES (%s, %s)""", (playerId, teamId))
        print(Player.getNameById(playerId), "added to team", Team.getNameById(teamId))
        return True

    def removePlayer(playerId, teamId):
        roundId = Team._getRoundIdByTeamId(teamId)
        if not roundId:
            print("Warning. addPlayer() round or team did not exist")
            return False
        oldTeamId = Team.getPlayerTeamId(playerId, roundId)
        if oldTeamId:
            Team.cur.execute("""DELETE FROM team_players
                WHERE team_id = %s AND player_id = %s""", (oldTeamId, playerId))
        return True

# gets
    def _getIdByName(teamName, roundId):
        Team.cur.execute("""SELECT team_id
            FROM team_list
            WHERE round_id = %s AND team_name = %s""", (roundId, teamName))
        return iterateZero(Team.cur.fetchone())

    def getNameById(teamId):
        Team.cur.execute("""SELECT team_name
            FROM team_list
            WHERE team_id = %s""", [teamId])
        return iterateZero(Team.cur.fetchone())

    def getColorById(teamId):
        Team.cur.execute("""SELECT team_color
            FROM team_list
            WHERE team_id = %s""", [teamId])
        color = iterateZero(Team.cur.fetchone())
        if not color:
            return 'FFFFFF'
        return color

    def _getRoundIdByTeamId(teamId):
        Team.cur.execute("""SELECT round_id
            FROM team_list
            WHERE team_id = %s""", [teamId])
        return iterateZero(Team.cur.fetchone())

    def getPlayerTeamId(playerId, roundId):
        Team.cur.execute("""SELECT team_id 
            FROM team_players 
            WHERE player_id = %s AND team_id IN 
            (SELECT team_id FROM team_list WHERE round_id = %s)""", (playerId, roundId))
        return iterateZero(Team.cur.fetchone())

    def getTeamlessPlayerIdList(roundId):
        teamlessPlayers = []
        for id in Player.getAllPlayerIds():
            if not Team.getPlayerTeamId(id, roundId):
                teamlessPlayers.append(id)
        return teamlessPlayers

# get lists
    def getTeamPlayerIdList(teamId):
        Team.cur.execute("""SELECT player_id
            FROM team_players
            WHERE team_id = %s""", [teamId])
        playerIds = Team.cur.fetchall()
        return sum(playerIds, ())

    def getTeamsIdList(roundId):
        Team.cur.execute("""SELECT team_id
            FROM team_list
            WHERE round_id = %s""", [roundId])
        teamIds = Team.cur.fetchall()
        return sum(teamIds, ())

