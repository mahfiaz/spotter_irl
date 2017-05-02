from .code import Code
from .event import Event, EventType
from .player import Player
from .round import Round
from .team import Team
import game_config
from game_config import msgCellular, msgBase

import json
import time
import re
import pprint
from threading import Timer


class Sms:
    _count = 0
    def send(mobile, data, sendStats = False):
        if isinstance(mobile, str):
            if mobile.isdigit():
                if sendStats:
                    print("     SMS:", mobile, data, Action.getTeamPlayerStatsString(Player.getMobileOwnerId(mobile)))
                else:
                    print("     SMS:", mobile, data)
                Sms._count += 1
        else:
            print(" Errror! send sms", mobile, data)

    def notSignedUp(mobile):
        Sms.send(mobile, msgCellular['notSignedUp'].format(mobile))

    def senderJailed(mobile, name, jailCode):
        Sms.send(mobile, msgCellular['senderJailed'].format(name, jailCode), sendStats = True)

    def victimJailed(senderMobile, senderName, victimMobile, victimName, jailCode):
        Sms.send(victimMobile, msgCellular['victimJailedVictim'].format(victimName, senderName, jailCode), sendStats = True)
        Sms.send(senderMobile, msgCellular['victimJailedSender'].format(senderName, victimName, victimName), sendStats = True)

    def missed(mobile, name):
        Sms.send(mobile, msgCellular['missed'].format(name), sendStats = True)

    def oldCode(mobile, nameSender, nameVictim):
        Sms.send(mobile, msgCellular['oldCode'].format(nameSender, nameVictim), sendStats = True)

    def exposedSelf(mobile, name, jailCode):
        Sms.send(mobile, msgCellular['exposedSelf'].format(name, jailCode), sendStats = True)

    def spotMate(senderMobile, senderName, victimMobile, victimName, jailCode):
        Sms.send(senderMobile, msgCellular['spotMateSender'].format(senderName, victimName), sendStats = True)
        Sms.send(victimMobile, msgCellular['spotMateVictim'].format(victimName, jailCode), sendStats = True)

    def spotted(senderMobile, senderName, victimMobile, victimName, jailCode):
        Sms.send(senderMobile, msgCellular['spottedSender'].format(senderName, victimName), sendStats = True)
        Sms.send(victimMobile, msgCellular['spottedVictim'].format(victimName, jailCode), sendStats = True)

    def touched(senderMobile, senderName, victimMobile, victimName, jailCode):
        Sms.send(senderMobile, msgCellular['touchedSender'].format(senderName, victimName), sendStats = True)
        Sms.send(victimMobile, msgCellular['touchedVictim'].format(victimName, jailCode), sendStats = True)

    def fleeingProtectionOver(mobile, name):
        Sms.send(mobile, msgCellular['fleeingProtectionOver'].format(name))

    def noActiveRound(mobile, nextIn):
        Sms.send(mobile, msgCellular['noActiveRound'].format(nextIn))

    def roundStarted(mobile, roundName):
        Sms.send(mobile, msgCellular['roundStarted'].format(roundName))

    def roundEnding(mobile, roundName, timeLeft):
        Sms.send(mobile, msgCellular['roundEnding'].format(roundName, timeLeft), sendStats = True)

    def roundEnded(mobile, roundName):
        Sms.send(mobile, msgCellular['roundEnded'].format(roundName), sendStats = True)

    def playerAdded(mobile, name, jailCode):
        Sms.send(mobile, msgCellular['playerAdded'].format(name, jailCode))


class BaseMsg:

    def send(msg):
        print("        Base Msg:", msg)

    def fleeingCodeMismatch():
        BaseMsg.send(msgBase['fleeingCodeMismatch'])

    def fledSuccessful(name, minutes):
        BaseMsg.send(msgBase['fledSuccessful'].format(name, minutes))

    def cantFleeFromLiberty(name):
        BaseMsg.send(msgBase['cantFleeFromLiberty'].format(name))

    def playerAdded(name):
        BaseMsg.send(msgBase['playerAdded'].format(name))

    def playerNotUnique(name, mobile, email):
        BaseMsg.send(msgBase['playerNotUnique'].format(name, mobile, email))

    def mobileNotDigits(mobile):
        BaseMsg.send(msgBase['mobileNotDigits'].format(mobile))

    def roundStarted():
        BaseMsg.send(msgBase['roundStarted'].format(Round.getName(Round.getActiveId())))

    def roundEnding(timeLeft):
        BaseMsg.send(msgBase['roundEnding'].format(Round.getName(Round.getActiveId()), timeLeft))

    def roundEnded():
        BaseMsg.send(msgBase['roundEnded'].format(Round.getName(Round.getActiveId())))


class Action:
    compactPrint = pprint.PrettyPrinter(width=41, compact=True)
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
        if not mobile.isdigit():
            BaseMsg.mobileNotDigits(mobile)
            return
        name = re.sub('[^a-zA-Z0-9-_]', '', name)
        email = re.sub('[^a-zA-Z0-9-_@.]', '', email)
        newPlayerId = Player.add(name, mobile, email)
        if newPlayerId:
            Event.addPlayer(newPlayerId)
            BaseMsg.playerAdded(name)
            Sms.playerAdded(mobile, name, Player.getFleeingCode(newPlayerId))
        else:
            BaseMsg.playerNotUnique(name, mobile, email)
        return newPlayerId

    def addTeams(roundId):
        for teamName in game_config.team_names:
            Team.add(teamName, roundId)

# handle code
    def handleCodeValidate(mobile, code):
        if (not mobile) or (not code):
            print("Warning. handleCode input missing", mobile, code)
            return
        if isinstance(code, str):
            if '?' in code:
                print("Mode: stats requested")
                return
            code = int(re.sub('[^0-9?]', '', code))
        mobile = re.sub('[^0-9+]', '', mobile)
        if (not mobile) or (not code):
            print("Warning. mobile or code is total chibberish")
            return
        Action._handleCode(mobile, code)

    def _handleCode(mobile, code):
        senderId = Player.getMobileOwnerId(mobile)
        senderJailed = Event.isPlayerJailed(senderId)
        senderName = Player.getNameById(senderId)
        if not senderId:
            Event.addObscureMessage(mobile, code)
            Sms.notSignedUp(mobile)
            return
        if not Round.updateActiveId():
            Sms.noActiveRound(mobile, Round._getStartTimeOfNext())
            addObscureMessage(senderId, code)
            return
        code = int(code)
        if senderJailed:
            Sms.senderJailed(mobile, senderName, Player.getFleeingCode(senderId))
            # store event too
            return
        victimId, codeValid = Code.getVictimIdByCode(code)
        if not victimId:
            # first add event, then update stats and then send sms with updated stats
            Event.addFailedSpot(senderId, code)
            Action.updateStats()
            Sms.missed(mobile, Player.getNameById(senderId))
            return
        victimJailed = Event.isPlayerJailed(victimId)
        victimName = Player.getNameById(victimId)
        victimMobile = Player.getMobileById(victimId)
        if not codeValid:
            Event.addWasAimedWithOldCode(victimId, code)
            Sms.oldCode(mobile, senderName, victimName)
            return
        if victimJailed:
            Sms.victimJailed(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
            return
        assert type(senderId) == type(victimId)
        if senderId == victimId:
            Event.addExposeSelf(victimId)
            Action.updateStats()
            Sms.exposedSelf(mobile, senderName, Player.getFleeingCode(senderId))
            return
        if Team.getPlayerTeamId(senderId, Round.getActiveId()) == Team.getPlayerTeamId(victimId, Round.getActiveId()):
            Event.addSpotMate(senderId, victimId)
            Action.updateStats()
            Sms.spotMate(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
            return
        else:
            if Code._isValidSpotCodeFormat(code):
                Event.addSpot(senderId, victimId)
                Action.updateStats()
                Sms.spotted(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
            elif Code._isValidTouchCodeFormat(code):
                Event.addTouch(senderId, victimId)
                Action.updateStats()
                Sms.touched(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))


# flee
    def fleePlayerWithCode(fleeingCode):
        playerId = Player.checkFleeingCode(fleeingCode)
        if playerId:
            Action._flee(playerId)
        else:
            BaseMsg.fleeingCodeMismatch()

    def _fleeTimerCall(playerId):
        Sms.fleeingProtectionOver(Player.getMobileById(playerId), Player.getNameById(playerId))

    def _flee(playerId):
        if Player.getNameById(playerId):
            if Event.isPlayerJailed(playerId):
                Player._generateFleeingCode(playerId)
                Event.addFlee(playerId)
                Code.generateNewCodes(playerId)
                Timer(game_config.player_fleeingProtectionTime, Action._fleeTimerCall, (playerId,)).start()
                BaseMsg.fledSuccessful(Player.getNameById(playerId), round(game_config.player_fleeingProtectionTime / 60, 1))
                return playerId
            else:
                BaseMsg.cantFleeFromLiberty(Player.getNameById(playerId))
                return False

# stats
    def updateStats():
        stats = Action._calcAllStats(Round.getActiveId())
        Action._storeStats(stats)
        events = Action.getEventList(Round.getActiveId(), 15)
        Action._storeEvents(events)
        Action.printIndented(stats)
        Action.printIndented(events)
        Action.printIndented(Action._getTeamScores(stats))

    def _getPlayerStats(playerId, roundId):
        stats = {
            'name'              : Player.getNameById(playerId),
            'nowInLiberty'      : not Event.isPlayerJailed(playerId),
            'spotCount'         : Event.getPlayerSpotCount(playerId, roundId),
            'touchCount'        : Event.getPlayerTouchCount(playerId, roundId),
            'jailedCount'       : Event.getPlayerJailedCount(playerId, roundId),
            'disloyality'       : Event.getPlayerDisloyalityCount(playerId, roundId),
            'lastActivity'      : Event.getPlayerLastActivity(playerId).strftime(game_config.database_dateformat)
        }
        stats['score'] = stats['spotCount'] + 2 * stats['touchCount'] - stats['jailedCount'] - stats['disloyality']
        return stats

    def _getTeamStats(teamId, roundId):
        players = Team.getTeamPlayerIdList(teamId)
        teamStats = {
            'name'              : Team.getNameById(teamId),
            'nowInLiberty'      : 0,
            'spotCount'         : 0,
            'touchCount'        : 0,
            'jailedCount'       : 0,
            'disloyality'       : 0,
            'score'             : 0}
        playersStats = []
        for playerId in players:
            person = Action._getPlayerStats(playerId, roundId)
            playersStats.append(person)
            teamStats['nowInLiberty'] += person['nowInLiberty']
            teamStats['spotCount'] += person['spotCount']
            teamStats['touchCount'] += person['touchCount']
            teamStats['jailedCount'] += person['jailedCount']
            teamStats['disloyality'] += person['disloyality']
            teamStats['score'] += person['score']
        teamStats['players'] = playersStats
        return teamStats

    def _calcAllStats(roundId):
        teamIds = Team.getTeamsIdList(roundId)
        allTeams = []
        for id in teamIds:
            allTeams.append(Action._getTeamStats(id, roundId))
        roundStats = {
            'roundId'           : roundId,
            'roundName'         : Round.getName(roundId),
            'roundStart'        : Round.getStartTime(roundId).strftime(game_config.database_dateformat),
            'roundEnd'          : Round.getEndTime(roundId).strftime(game_config.database_dateformat),
            'smsCount'          : Sms._count,
            'teams'             : allTeams}
        return roundStats

    def _storeStats(stats):
        if stats:
            with open('stats.json', 'w') as jsonFile:
                json.dump(stats, jsonFile, indent=4)

    def getRoundStats():
        with open('stats.json') as jsonFile:
            return json.load(jsonFile)

    def printIndented(stats):
        Action.compactPrint.pprint(stats)

    def _getTeamScores(stats):
        if stats:
            teams = stats['teams']
            teamScores = []
            for team in teams:
                teamScores.append({ 'name' : team['name'], 'score' : team['score'] })
            return teamScores

    def _getTeamScoreString():
        stats = Action.getRoundStats()
        if not stats:
            print("Warning. Stats could not be fetched")
            return ''
        teamScores = Action._getTeamScores(stats)
        result = ''
        for each in teamScores:
            result += ' {}:{}'.format(each['name'], each['score'])
        return result

    def _getPlayerScoreString(playerId):
        stats = Action._getPlayerStats(playerId, Round.getActiveId())
        if stats:
            return '{}:{}'.format(Player.getNameById(playerId), stats['score'])
        return ''

    def getTeamPlayerStatsString(playerId):
        return Action._getPlayerScoreString(playerId) + Action._getTeamScoreString()

#events
    def getEventList(roundId, rows):
        events = Event.getEventListRaw(roundId, rows)
        eventList = []
        for event in events:
            event, playerId, timestamp = event
            thisEvent = {}
            thisEvent['time'] = timestamp.strftime(game_config.database_dateformat)
            thisEvent['player1'] = { 'name' : Player.getNameById(playerId), 'team' : Team.getNameById(Team.getPlayerTeamId(playerId, roundId))}
            thisEvent['event'] = EventType(event).name
            player2Id = Event.getDidEventPair(event, timestamp)
            thisEvent['player2'] = { 'name' : Player.getNameById(player2Id), 'team' : Team.getNameById(Team.getPlayerTeamId(player2Id, roundId))}
            eventList.append(thisEvent)
        return eventList

    def _storeEvents(events):
        if events:
            with open('events.json', 'w') as jsonFile:
                json.dump(events, jsonFile, indent = 4)

    def getRoundEvents():
        with open('events.json') as jsonFile:
            return json.load(jsonFile)[0]

# round calls
    def _roundStartedCall():
        BaseMsg.roundStarted()
        for id in Player.getAllPlayerIds():
            mobile = Player.getMobileById(id)
            Sms.roundStarted(mobile, Round.getName(Round.getActiveId()))

    def _roundEndingCall(left):
        BaseMsg.roundEnding(left)
        for id in Player.getAllPlayerIds():
            mobile = Player.getMobileById(id)
            Sms.roundEnding(mobile, Round.getName(Round.getActiveId()), left)

    def _roundEndedCall():
        BaseMsg.roundEnded()
        for id in Player.getAllPlayerIds():
            mobile = Player.getMobileById(id)
            Sms.roundEnded(mobile, Round.getName(Round.getActiveId()))

# print
    def printPlayersDetailed():
        Player.cur.execute("""SELECT player_data.player_id, player_data.player_name, player_data.player_mobile, team_players.team_id, player_data.player_fleeing_code, code_list.spot_code, code_list.touch_code
            FROM player_data 
                JOIN code_list ON (player_data.player_code_id = code_list.code_id)
                JOIN team_players ON (player_data.player_id = team_players.player_id)
            """)
        rows = Player.cur.fetchall()
        for row in rows:
            (id, name, mobile, teamId, fleeingCode, spotCode, touchCode) = row
            print(" - ", id, mobile, teamId, fleeingCode, spotCode, touchCode, Event.isPlayerJailed(row[0]), name)
