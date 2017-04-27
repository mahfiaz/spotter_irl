from .code import Code
from .event import Event
from .player import Player
from .round import Round
from .team import Team

import time

class Action:

    def initAllOnce(cursor):
        Round.initOnce(cursor)
        Player.initOnce(cursor)
        Code.initOnce(cursor)
        Team.initOnce(cursor)
        Event.initOnce(cursor)

    def handleCode(mobile, code):
        senderId = Player.getMobileOwnerId(mobile)
        senderJailed = Event.isPlayerJailed(senderId)
        if not senderId:
            print("this player has not been signed up for the game", mobile)
            # send back sms "come to the base and sign up"
            #Event.addStrangeSms(mobile, code)
            return
        if not Round.updateActiveId():
            print("currently no active round. no action goes through")
            #send sms round starts at....
            addObscureMessage(senderId, code)
            return
        victimId, codeValid = Code.getVictimIdByCode(code)
        victimJailed = Event.isPlayerJailed(victimId)
        if senderJailed:
            print(senderId[0], " jailed, could not spot anybody")
            # sms: teleport to the base.
            return
        if not victimId:
            print(senderId[0], "had a missed hit")
            Event.addFailedSpot(senderId, code)
            Action.updateStats()
            return
        if not codeValid:
            print(victimId, "is either wearing old codes or ", senderId, " has a longtime memory")
            Event.addWasAimedWithOldCode(victimId, code)
            return
        if victimJailed:
            print(victimId[0], "victim jailed.", senderId[0], " is using old information")
            # sms victim: teleport to the base
            return
        if senderId == victimId:
            print(senderId[0], "exposed self to authorities")
            Event.addExposeSelf(victimId)
            Action.updateStats()
            # suicide sms
            return
        if Team.getPlayerTeamId(senderId, Round.getActiveId()) == Team.getPlayerTeamId(victimId, Round.getActiveId()):
            print(senderId[0], " did hit teammate ", victimId)
            Event.addSpotMate(senderId, victimId)
            Action.updateStats()
            # friendly fire warning sms
            return
        else:
            if Code._isValidSpotCodeFormat(code):
                print(senderId[0], " spotted ", victimId[0])
                Event.addSpot(senderId, victimId)
                # sms: successful spotting
            elif Code._isValidTouchCodeFormat(code):
                print(senderId[0], " touched ", victimId[0])
                Event.addTouch(senderId, victimId)
                # sms: successful touch
            Action.updateStats()

    def updateStats():
        pass

    def addPlayer(name, mobile, email):
        newPlayerId = Player.add(name, mobile, email)
        Event.addPlayer(newPlayerId)
        return newPlayerId

    def _flee(playerId):
        if Event.isPlayerJailed(playerId):
            Player._generateFleeingCode(playerId)
            Event.addFlee(playerId)
            Code.generateNewCodes(playerId)
            print(playerId, "fled!")
            return playerId
        else:
            print(playerId, "In liberty, couldnt flee!")
            return False

    def fleePlayerWithCode(playerId, fleeingCode):
        if Player.checkFleeingCode(playerId, fleeingCode):
            Action._flee(playerId)
        else:
            print("sorry, this fleeing code did not match!")

    def getPlayerStats(playerId, roundId):
#        roundId, name = Round.getActiveId()
        stats = [{
            'name'              : Player.getNameById(playerId)[0],
            'totalSpots'        : Event.getPlayerSpotTotalCount(playerId, roundId),
            'touchCount'        : Event.getPlayerTouchCount(playerId, roundId),
            'jailed'            : Event.getPlayerJailedCount(playerId, roundId),
            'teamDisloyality'   : Event.getPlayerDisloyalityCount(playerId, roundId),
            'accuracy'          : Event.getSpottingAccuracy(playerId, roundId),
            'lastActivity'      : Event.getPlayerLastActivity(playerId)
        }]
        return stats

    def getTeamStats(teamId, roundId):
        players = Team.getTeamPlayerIdList(teamId)
        teamStats = []
        for player in players:
            teamStats += Action.getPlayerStats(player, roundId)
        return teamStats

    def getAllStats(roundId):
        teams = Team.getTeamsIdNameList(roundId)
        print(teams)
        roundStats = []
        for team in teams:
            id, name = team
            roundStats += [{
            'teamName'          : name,
            'players'           : Action.getTeamStats(id, roundId)}]
        return roundStats

    def addTestTeams():
        Team.add("Sinised", Round.getActiveId())
        Team.add("Punased", Round.getActiveId())
        Team.add("Sinised", Round.getActiveId())

    def addPlayersToTeams():
        Team.addPlayer(1, Team.getIdByName('Sinised', Round.getActiveId()))
        Team.addPlayer(2, Team.getIdByName('Sinised', Round.getActiveId()))
        Team.addPlayer(3, Team.getIdByName('Punased', Round.getActiveId()))
        Team.addPlayer(4, Team.getIdByName('Punased', Round.getActiveId()))

    def addTestPlayers():
        dataDict = ({"name":"Ets2", "mobile":"111", "email":"ets@gail.cm"},
                {"name":"Vollts", "mobile":"222", "email":"Volts@gail.cm"},
                {"name":"KalleLalle", "mobile":"333", "email":"KAlli@gail.cm"},
                {"name":"lililii", "mobile":"444", "email":"KA3l3li@gail.cm"})
        for each in dataDict:
            Action.addPlayer(each['name'], each['mobile'], each['email'])
        Player.printDetailed()

#    def addTestAction():
#        for playerId in Player.getAllPlayerIds():
#            Code.generateNewCodes(playerId)
#            Action._flee(playerId)
#        Player.printDetailed()
#        Action.addTestAction2()

    def addTestAction():
        Player.printDetailed()

        for playerId in Player.getAllPlayerIds():
            Action.fleePlayerWithCode(playerId, Player.getFleeingCode(playerId))

        print("1-1")
        Action.handleCode(Player.getMobileById(1), Code.getSpotCodeByPlayerId(1))
        Action.fleePlayerWithCode(4, Player.getFleeingCode(4))
        Player.printDetailed()

        time.sleep(0.1)
        print("4-1")
        Action.handleCode(Player.getMobileById(4), Code.getSpotCodeByPlayerId(1))
        Player.printDetailed()
        Action.fleePlayerWithCode(1, Player.getFleeingCode(1))
        Player.printDetailed()

        time.sleep(0.1)

        print("4-1")
        Action.handleCode(Player.getMobileById(4), Code.getSpotCodeByPlayerId(1))
        Player.printDetailed()
        Action.fleePlayerWithCode(4, Player.getFleeingCode(4))
        Player.printDetailed()

        time.sleep(0.1)
        print("1-2")
        Action.handleCode(Player.getMobileById(1), Code.getSpotCodeByPlayerId(2))
        Player.printDetailed()
        Action.fleePlayerWithCode(2, Player.getFleeingCode(2))
        Action.fleePlayerWithCode(2, Player.getFleeingCode(1))
        Player.printDetailed()
        time.sleep(0.1)

        Action.fleePlayerWithCode(1, Player.getFleeingCode(1))
        Action.fleePlayerWithCode(3, Player.getFleeingCode(3))
        print("1-H3", Code.getTouchCodeByPlayerId(3))
        Action.handleCode(Player.getMobileById(1), Code.getTouchCodeByPlayerId(3))
        Player.printDetailed()
        Action.fleePlayerWithCode(1, Player.getFleeingCode(1))
        Player.printDetailed()
        time.sleep(0.1)

        Action.handleCode(Player.getMobileById(1), Code.getSpotCodeByPlayerId(4))
        Player.printDetailed()
        
