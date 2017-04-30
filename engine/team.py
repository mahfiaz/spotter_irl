#import player
from .player import Player
from .round import Round

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

    def add(teamName, roundId):
        if not Round.existingId(roundId):
            print("Error. Team", teamName, "not added, because roundId", roundId, "doesn't exist.")
            return
        if not Team.getIdByName(teamName, roundId):
            Team.cur.execute("""INSERT INTO team_list (team_name, round_id)
                VALUES (%s, %s)""", (teamName, roundId))
            print("Team", teamName, "added.")
            return Team.getIdByName(teamName, roundId)
        else:
            print("Warning! Team", teamName, "not added, it already exists.")

    def getIdByName(teamName, roundId):
        Team.cur.execute("""SELECT team_id
            FROM team_list
            WHERE round_id = %s AND team_name = %s""", (roundId, teamName))
        return Team.cur.fetchone()

    def getNameById(teamId):
        Team.cur.execute("""SELECT team_name
            FROM team_list
            WHERE team_id = %s""", [teamId])
        return Team.cur.fetchone()

    def _getRoundIdByTeamId(teamId):
        Team.cur.execute("""SELECT round_id
            FROM team_list
            WHERE team_id = %s""", [teamId])
        return Team.cur.fetchone()


#    def getTeamsList():
#        Team.cur.execute("""SELECT team_players.team_id, player_data.player_id, player_data.player_name
#            FROM team_players JOIN player_data ON (team_players.player_id = player_data.player_id)
#            WHERE team_players.team_id IN
#            (SELECT team_id FROM team_list)""")
#        teams = Team.cur.fetchall()
#        return teams

    def getTeamPlayerIdList(teamId):
        Team.cur.execute("""SELECT player_id
            FROM team_players
            WHERE team_id = %s""", [teamId])
        teams = Team.cur.fetchall()
        return teams

#team_id, team_name
#WHERE round_id = %s
    def getTeamsIdNameList(roundId):
        Team.cur.execute("""SELECT team_id, team_name
            FROM team_list
            WHERE round_id = %s""", [roundId])
        return Team.cur.fetchall()

    def getPlayerTeamId(playerId, roundId):
        Team.cur.execute("""SELECT team_id 
            FROM team_players 
            WHERE player_id = %s AND team_id IN 
            (SELECT team_id FROM team_list WHERE round_id = %s)""", (playerId, roundId))
        return Team.cur.fetchone()

    def removePlayer(playerId, roundId):
        if Team.getPlayerTeamId(playerId, roundId):
            Team.cur.execute("""DELETE FROM team_players
                WHERE round_id = %s AND player_id = %s""", (roundId, playerId))

    def addPlayer(playerId, teamId):
        Team.removePlayer(playerId, Team._getRoundIdByTeamId(teamId))
        Team.cur.execute("""INSERT INTO team_players (player_id, team_id)
            VALUES (%s, %s)""", (playerId, teamId))
        print("Player ", Player.getNameById(playerId), " added to ", Team.getNameById(teamId))

