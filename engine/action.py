from .code import Code
from .event import Event
from .player import Player
from .round import Round
from .team import Team
import game_config

import json
import time
from threading import Timer

class Action:

# init
    def initAllOnce(cursor):
        Round.initOnce(cursor)
        Player.initOnce(cursor)
        Code.initOnce(cursor)
        Team.initOnce(cursor)
        Event.initOnce(cursor)
        Round.setCallbacks(roundStarted = Action._roundStartedCall, roundEnding = Action._roundEndingCall, roundEnded = Action._roundEndedCall)

# modify
    def addPlayer(name, mobile, email):
        newPlayerId = Player.add(name, mobile, email)
        if newPlayerId:
            Event.addPlayer(newPlayerId)
        return newPlayerId

# handle code
    def handleCode(mobile, code):
        senderId = Player.getMobileOwnerId(mobile)
        senderJailed = Event.isPlayerJailed(senderId)
        if not senderId:
            print("this player has not been signed up for the game", mobile)
            # send back sms "come to the base and sign up."
            Event.addObscureMessage(mobile, code)
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
            # suicide sms, enekas
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

# flee
    def fleePlayerWithCode(playerId, fleeingCode):
        if Player.checkFleeingCode(playerId, fleeingCode):
            Action._flee(playerId)
        else:
            print("sorry, this fleeing code did not match!")

    def _fleeTimerCall(playerId):
        print(playerId, ", your fleeing protection is over, make the codes visible!")

    def _flee(playerId):
        if Event.isPlayerJailed(playerId):
            Player._generateFleeingCode(playerId)
            Event.addFlee(playerId)
            Code.generateNewCodes(playerId)
            Timer(game_config.player_fleeingProtectionTime, Action._fleeTimerCall, (playerId,)).start()
            print(playerId, "fled!")
            return playerId
        else:
            print(playerId, "In liberty, couldnt flee!")
            return False

# stats
    def updateStats():
#        roundSecondsLeft = Round.getActiveSecondsLeft()
        stats = Action._calcAllStats(Round.getActiveId())
        Action._storeStats(stats)

    def getPlayerStats(playerId, roundId):
        stats = [{
            'name'              : Player.getNameById(playerId)[0],
            'totalSpots'        : Event.getPlayerSpotTotalCount(playerId, roundId),
            'touchCount'        : Event.getPlayerTouchCount(playerId, roundId),
            'jailed'            : Event.getPlayerJailedCount(playerId, roundId),
            'teamDisloyality'   : Event.getPlayerDisloyalityCount(playerId, roundId),
            'accuracy'          : Event.getSpottingAccuracy(playerId, roundId),
            'lastActivity'      : Event.getPlayerLastActivity(playerId).strftime(game_config.database_dateformat)
        }]
        return stats

    def getTeamStats(teamId, roundId):
        players = Team.getTeamPlayerIdList(teamId)
        teamStats = []
        for player in players:
            teamStats += Action.getPlayerStats(player, roundId)
        return teamStats

    def _calcAllStats(roundId):
        teamIds = Team.getTeamsIdList(roundId)
        allTeams = []
        for id in teamIds:
            allTeams.append([{
                'teamId'        : id,
                'teamName'      : Team.getNameById(id),
                'players'       : Action.getTeamStats(id, roundId)}])
        roundStats = [{
            'roundId'           : roundId,
            'roundName'         : Round.getName(roundId),
            'roundEnd'          : Round._getEndTimeOfActive().strftime(game_config.database_dateformat),
            'teams'             : allTeams}]
        return roundStats

    def _storeStats(stats):
        if stats:
            with open('stats.json', 'w') as jsonFile:
                json.dump(stats, jsonFile)

    def getRoundStats():
        with open('stats.json') as jsonFile:
            stats = json.load(jsonFile)[0]
            return stats

# round calls
    def _roundStartedCall():
        print("Round", Round.getName(Round.getActiveId())[0], "started!")

    def _roundEndingCall(left):
        print("Round", Round.getName(Round.getActiveId())[0], "is ending. minutes left:", left)

    def _roundEndedCall():
        print("Round", Round.getName(Round.getActiveId())[0], "is over. Get to the base!")

