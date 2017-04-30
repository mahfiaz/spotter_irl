#import player
from .player import Player
from .round import Round
from .helper import iterateZero

class Team:

# init
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

# modify teams
    def add(teamName, roundId):
        if not Round.existingId(roundId):
            print("Error. Team", teamName, "not added, because roundId", roundId, "doesn't exist.")
            return
        if not Team._getIdByName(teamName, roundId):
            Team.cur.execute("""INSERT INTO team_list (team_name, round_id)
                VALUES (%s, %s)""", (teamName, roundId))
            print("Team", teamName, "added.")
            return Team._getIdByName(teamName, roundId)
        else:
            print("Warning! Team", teamName, "not added, it already exists.")

    def addPlayer(playerId, teamId):
        Team.removePlayer(playerId, Team._getRoundIdByTeamId(teamId))
        Team.cur.execute("""INSERT INTO team_players (player_id, team_id)
            VALUES (%s, %s)""", (playerId, teamId))
        print("Player ", Player.getNameById(playerId), " added to ", Team.getNameById(teamId))

    def removePlayer(playerId, roundId):
        if Team.getPlayerTeamId(playerId, roundId):
            Team.cur.execute("""DELETE FROM team_players
                WHERE round_id = %s AND player_id = %s""", (roundId, playerId))

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

# get lists
    def getTeamPlayerIdList(teamId):
        Team.cur.execute("""SELECT player_id
            FROM team_players
            WHERE team_id = %s""", [teamId])
        teams = Team.cur.fetchall()
        return teams

    def getTeamsIdList(roundId):
        Team.cur.execute("""SELECT team_id
            FROM team_list
            WHERE round_id = %s""", [roundId])
        return Team.cur.fetchall()

