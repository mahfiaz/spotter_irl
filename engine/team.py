
class Team:
    name = None
    color = None
    round = None

    ready = False

    def __init__(self, parent, name=None, color=None):
        self.parent = parent
        self.log = parent.log
        self.cur = parent.cur

# modify teams
    def add(teamName, color, roundId):
        if not Round.existingId(roundId):
            print("Warning. Team", teamName, "not added, because roundId", roundId, "doesn't exist.")
            return
        if not Team._getIdByName(teamName, roundId):
            Team.cur.execute("""INSERT INTO teams (name, round_id, color)
                VALUES (%s, %s, %s)""", (teamName, roundId, color))
            print("Team", teamName, "added to round", Round.getName(roundId))
            return Team._getIdByName(teamName, roundId)
        else:
            print("Warning! Team", teamName, "not added, it already exists.")

    def add(self, player):
        if not Team.removePlayer(playerId, teamId):
            return
        Team.cur.execute("""INSERT INTO team_players (pid, team_id)
            VALUES (%s, %s)""", (playerId, teamId))
        print(Player.getNameById(playerId), "added to team", Team.getNameById(teamId))
        return True

    def remove(self, player):
        roundId = Team._getRoundIdByTeamId(teamId)
        if not roundId:
            print("Warning. addPlayer() round or team did not exist")
            return False
        oldTeamId = Team.getPlayerTeamId(playerId, roundId)
        if oldTeamId:
            Team.cur.execute("""DELETE FROM team_players
                WHERE team_id = %s AND pid = %s""", (oldTeamId, playerId))
        return True

class Teams:
    current = None

    def __init__(self, parent):
        self.parent = parent
        self.cur = parent.cur
        self.log = parent.log

        self.teams = {}

        # Fixed teams. Good enough.
        for teamname, color in [('CT', 'blue'), ('TR', 'red')]:
            self.teams[teamname] = Team(self, teamname, color)

    def find(self, name = None, round_id = None):
        pass

    def _getIdByName(teamName, roundId):
        Team.cur.execute("""SELECT team_id
            FROM teams
            WHERE round_id = %s AND name = %s""", (roundId, teamName))
        return iterateZero(Team.cur.fetchone())

# get lists
    def getTeamPlayerIdList(teamId):
        Team.cur.execute("""SELECT pid
            FROM team_players
            WHERE team_id = %s""", [teamId])
        playerIds = Team.cur.fetchall()
        return sum(playerIds, ())

    def getTeamlessPlayerIdList(roundId):
        teamlessPlayers = []
        for id in Player.getAllPlayerIds():
            if not Team.getPlayerTeamId(id, roundId):
                teamlessPlayers.append(id)
        return teamlessPlayers

    def getTeamsIdList(roundId):
        Team.cur.execute("""SELECT team_id
            FROM teams
            WHERE round_id = %s""", [roundId])
        teamIds = Team.cur.fetchall()
        return sum(teamIds, ())

    def init_database(cursor):
        cursor.execute("""DROP TABLE IF EXISTS team""")
        cursor.execute("""CREATE TABLE team (
            team_id serial PRIMARY KEY,
            name VARCHAR(30) NOT NULL,
            color CHAR(6),
            round_id int)""")
        cursor.execute("""DROP TABLE IF EXISTS team_players""")
        cursor.execute("""CREATE TABLE team_players (
            pid int,
            team_id int,
            added timestamp DEFAULT statement_timestamp())""")
