from .code import Code
from .event import Event, EventType
from .player import Player
from .round import Round
from .team import Team
from .message import Sms, BaseMsg
from .spawn import Spawn, Base
import game_config

import json
import time
import re
import pprint
from threading import Timer



class Action:
    compactPrint = pprint.PrettyPrinter(width=41, compact=True)
    printer_queue = None
# init
    def initAllDB(cursor):
        Round.initDB(cursor)
        Player.initDB(cursor)
        Code.initDB(cursor)
        Team.initDB(cursor)
        Event.initDB(cursor)
        Stats.updateStats()
        Spawn.initDB(cursor)
        Base.initDB(cursor)

    def initAllConnect(cursor, sms_queue, printer_queue):
        Round.initConnect(cursor)
        Player.initConnect(cursor)
        Code.initConnect(cursor)
        Team.initConnect(cursor)
        Event.initConnect(cursor)
        Round.setCallbacks(roundStarted = Action._roundStartedCall, roundEnding = Action._roundEndingCall, roundEnded = Action._roundEndedCall)
        Stats.updateStats()
        Sms.queue = sms_queue
        Sms.setCallback(Stats.getTeamPlayerStatsStringByMobile)
        Spawn.initConnect(cursor)
        Base.initConnect(cursor)
        Action.printer_queue = printer_queue

# modify
    def addPlayerWOEmail(name, mobile):
        return Action.addPlayer(name, mobile, '')

    def addPlayer(name, mobile, email):
        if not mobile.isdigit():
            BaseMsg.mobileNotDigits(mobile)
            return
        name = re.sub('[^a-zA-Z0-9-_]+', '', name)
        email = re.sub('[^a-zA-Z0-9-_@\.]+', '', email)
        newPlayerId = Player.add(name, mobile, email)
        if newPlayerId:
            Event.addPlayer(newPlayerId)
            BaseMsg.playerAdded(name)
            Sms.playerAdded(mobile, name, Player.getFleeingCode(newPlayerId))
            Stats.updateStats()
        else:
            BaseMsg.playerNotUnique(name, mobile, email)
        return newPlayerId

    def addPlayerToTeam(name, teamName):
        if not Round.getActiveId():
            print("Warning! addPlayerToTeam(). no active round")
            return
        playerId = Player._getIdByName(name)
        if not playerId:
            print("Warning! addPlayerToTeam(). no player found")
            return
        if playerId == Player.getMasterId():
            print("Warning! MasterPlayer can't be added to team.")
            return
        if not Team._getIdByName(teamName, Round.getActiveId()):
            print("Warning! addPlayerToTeam(). no team found")
            return
        teamId = Team._getIdByName(teamName, Round.getActiveId())
        if Team.addPlayer(playerId, teamId):
            Code.generateNewCodes(playerId)
            Event.addPlayerToTeam(playerId)
        Stats.updateStats()

    def addTeamsToAllRounds():
        for roundId in Round.getRoundIdList():
            Action._addConfiguredTeams(roundId)

    def _addConfiguredTeams(roundId):
        for team in game_config.teams:
            Team.add(team['name'], team['color'], roundId)

# handle code

    def _codeValidate(code):
        if not code:
            print("Warning. code input missing", code)
            return
        if isinstance(code, str):
            code = re.sub('[^0-9]+', '', code)
            if code:
                return int(code)

    def _mobileValidate(mobile):
        if not mobile:
            print("Warning. mobile input missing", mobile)
            return
        assert isinstance(mobile, str)
        return re.sub('[^0-9+]+', '', mobile)

    def _hashValidate(hash):
        if not hash:
            print("Warning. hash input missing", hash)
            return
        assert isinstance(hash, str)
        return re.sub('[^a-z0-9]+', '', hash)


    def handleSms(mobile, message):
        mobile = Action._mobileValidate(mobile)
        code = Action._codeValidate(message)
        senderId = Player.getMobileOwnerId(mobile)
        Action._handleCode(senderId, code, byMobile = True)
        print('Received SMS', mobile, message)

    def handleWeb(hash, code):
        hash = Action._hashValidate(hash)
        code = Action._codeValidate(code)
        senderId = Player.getIdByHash(hash)
        Action._handleCode(senderId, code, byMobile = False)

    def _handleCode(senderId, code, byMobile):
        mobile = Player.getMobileById(senderId)
        senderJailed = Event.isPlayerJailed(senderId)
        senderName = Player.getNameById(senderId)
        if not senderId:
            Event.addObscureMessage(senderId, code)
            if byMobile and mobile:
                Sms.notSignedUp(mobile)
            return
        if not Round.updateActiveId() or not code:
            Event.addObscureMessage(senderId, code)
            if byMobile:
                Sms.noActiveRound(mobile, Round._getStartTimeOfNext())
            return
        if not Team.getPlayerTeamId(senderId, Round.getActiveId()):
            Sms.alertGameMaster(senderName + " not added to any team! Please add!")
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
            Stats.updateStats()
            Sms.missed(mobile, Player.getNameById(senderId))
            return
        if not Team.getPlayerTeamId(victimId, Round.getActiveId()):
            Sms.alertGameMaster(Player.getNameById(victimId) + " not added to any team! Please add!")
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
            Stats.updateStats()
            Sms.exposedSelf(mobile, senderName, Player.getFleeingCode(senderId))
            return
        if Team.getPlayerTeamId(senderId, Round.getActiveId()) == Team.getPlayerTeamId(victimId, Round.getActiveId()):
            Event.addSpotMate(senderId, victimId)
            Stats.updateStats()
            Sms.spotMate(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
            return
        else:
            if Code._isValidSpotCodeFormat(code):
                Event.addSpot(senderId, victimId)
                Stats.updateStats()
                Sms.spotted(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
            elif Code._isValidTouchCodeFormat(code):
                Event.addTouch(senderId, victimId)
                Stats.updateStats()
                Sms.touched(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))

    def sayToMyTeam(playerId, message):
        if not playerId:
            return
        if Player.isBannedChat(playerId):
            print("Banned", Player.getNameById(playerId), "wanted to say:", message)
            return
        teamId = Team.getPlayerTeamId(playerId, Round.getActiveId())
        if playerId == Player.getMasterId():
            teamId = 0
        message = re.sub('[^A-Za-z0-9 \.,:;\-\?!#/ÕõÄäÖöÜü]', '', message)
        message = message[:60]
        print(Player.getNameById(playerId), "said ", message)
        Event.addChatMessage(playerId, teamId, message)
        Stats.updateEvents()

    def masterAnnounces(message):
        Action.sayToMyTeam(Player.getMasterId(), message)

# flee
    def fleePlayerWithCode(fleeingCode):
        code = Action._codeValidate(fleeingCode)
        if not code:
            return
        if not Round.getActiveId():
            print("Warning. No active team. No fleeing for" ,fleeingCode)
            return
        playerId = Player.checkFleeingCode(code)
        if playerId:
            if not Team.getPlayerTeamId(playerId, Round.getActiveId()):
                print("Warning. You are not in a team. No fleeing." ,fleeingCode)
                return
            Action._flee(playerId)
            Stats.updateStats()
            # Print
            Action.printer_queue.put(Action.prepareDataForPrinter(playerId))
            #sms_outgoing.put('tore')
        else:
            BaseMsg.fleeingCodeMismatch()

    def prepareDataForPrinter(playerId):
        teamId = Team.getPlayerTeamId(playerId, Round.getActiveId())
        data = {
            'player' : {
                'name' : Player.getNameById(playerId),
                'spotcode': Code.getSpotCodeByPlayerId(playerId),
                'touchcode': Code.getTouchCodeByPlayerId(playerId),
                'team': { 'name': Team.getNameById(teamId), 'color': Team.getColorById(teamId) },
            },
            'printer': 'PDF',
            'eventlist': Action.eventListFlatten(Stats.getRoundEvents()),
            'teamScores' : Stats._getTeamScores(Stats.getRoundStats())
        }
        return data

    def eventListFlatten(eventlist):
        output = []
        for event in eventlist:
            if event['visible'] == 'All':
                line = ''
                dlist = [event['time'], event['text1']['text'], event['text2']['text'], event['text3']['text']]
                for el in dlist:
                    if el:
                        line += el + " "
                output.append(line)
        return output

    def _fleeTimerCall(mobile, name):
        Sms.fleeingProtectionOver(mobile, name)

    def _flee(playerId):
        if Player.getNameById(playerId):
            if Event.isPlayerJailed(playerId):
                Player._generateFleeingCode(playerId)
                Event.addFlee(playerId)
                Code.generateNewCodes(playerId)
                timer = Timer(game_config.player_fleeingProtectionTime, Action._fleeTimerCall, (Player.getMobileById(playerId), Player.getNameById(playerId),))
                timer.daemon=True
                timer.start()
                BaseMsg.fledSuccessful(Player.getNameById(playerId), round(game_config.player_fleeingProtectionTime / 60, 1))
                return playerId
            else:
                BaseMsg.cantFleeFromLiberty(Player.getNameById(playerId))
                return False

    def _unbanAllChats():
        for playerId in Player.getAllPlayerIds():
            Player.unbanChat(playerId)

# round calls
    def _roundStartedCall(mobileNameList, roundName):
        Action.masterAnnounces("Lahing " + roundName + " algas.")
#        BaseMsg.roundStarted()
        for (mobile, name) in mobileNameList:
            Sms.roundStarted(mobile, roundName)
        for id in Player.getAllPlayerIds():
            Player.unbanChat(id)


    def _roundEndingCall(mobileNameList, roundName, left):
        Action.masterAnnounces("Lahing " + roundName + " lõpeb " + left + " min pärast. Tule autasustamisele baasi.")
#        BaseMsg.roundEnding(left)
        for (mobile, name) in mobileNameList:
            Sms.roundEnding(mobile, roundName, left)


    def _roundEndedCall(mobileNameList, roundName):
        Action.masterAnnounces("Lahing " + roundName + " lõppes. Oled oodatud baasi autasustamisele.")
#        BaseMsg.roundEnded()
        for (mobile, name) in mobileNameList:
            Sms.roundEnded(mobile, roundName)


class Stats:
    def updateStats():
        stats = Stats._calcAllStats(Round.getActiveId())
        Stats._storeStats(stats)
        Stats.updateEvents()

    def updateEvents():
        events = Stats.getEventList(Round.getActiveId(), 15)
        Stats._storeEvents(events)

    def printStats():
        if not Round.getActiveId():
            print("Warning. printStats() no active round")
            return
        stats = Stats.getRoundStats()
        events = Stats.getRoundEvents()
        Stats.printIndented(stats)
        Stats.printIndented(events)
        Stats.printIndented(Stats._getTeamScores(stats))
        Stats.printPlayersDetailed()

    def _getPlayerStats(playerId, roundId):
        stats = {
            'name'              : Player.getNameById(playerId),
            'nowInLiberty'      : not Event.isPlayerJailed(playerId),
            'spotCount'         : Event.getPlayerSpotCount(playerId, roundId),
            'touchCount'        : Event.getPlayerTouchCount(playerId, roundId),
            'jailedCount'       : Event.getPlayerJailedCount(playerId, roundId),
            'disloyality'       : Event.getPlayerDisloyalityCount(playerId, roundId),
            'lastActivity'      : Event.getPlayerLastActivityFormatted(playerId)
        }
        stats['score'] = stats['spotCount'] + 2 * stats['touchCount'] - stats['disloyality']
        return stats

    def _getTeamStats(teamId, roundId):
        players = Team.getTeamPlayerIdList(teamId)
        teamStats = {
            'name'              : Team.getNameById(teamId),
            'color'             : Team.getColorById(teamId),
            'nowInLiberty'      : 0,
            'spotCount'         : 0,
            'touchCount'        : 0,
            'jailedCount'       : 0,
            'disloyality'       : 0,
            'score'             : 0}
        playersStats = []
        for playerId in players:
            person = Stats._getPlayerStats(playerId, roundId)
            playersStats.append(person)
            teamStats['nowInLiberty'] += person['nowInLiberty']
            teamStats['spotCount'] += person['spotCount']
            teamStats['touchCount'] += person['touchCount']
            teamStats['jailedCount'] += person['jailedCount']
            teamStats['disloyality'] += person['disloyality']
            teamStats['score'] += person['score']
        teamStats['players'] = playersStats
        return teamStats

    def _getTeamplessPlayerStats(roundId):
        teamless = []
        for player in Team.getTeamlessPlayerIdList(roundId):
            print(player, Player.getMasterId())
            if not (player == Player.getMasterId()):
                teamless.append(Stats._getPlayerStats(player, roundId))
        return teamless

    def _calcAllStats(roundId):
        if not roundId:
            return { 'roundName' : None }
        teamIds = Team.getTeamsIdList(roundId)
        allTeams = []
        for id in teamIds:
            allTeams.append(Stats._getTeamStats(id, roundId))
        roundStats = {
            'roundName'         : Round.getName(roundId),
            'roundStart'        : Round.getStartTime(roundId).strftime(game_config.database_dateformat),
            'roundEnd'          : Round.getEndTime(roundId).strftime(game_config.database_dateformat),
            'smsCount'          : Sms._count,
            'teams'             : allTeams,
            'teamlessPlayers'   : Stats._getTeamplessPlayerStats(roundId) }
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
        stats = Stats.getRoundStats()
        if not stats:
            print("Warning. Stats could not be fetched")
            return ''
        teamScores = Stats._getTeamScores(stats)
        result = ''
        for each in teamScores:
            result += ' {}:{}'.format(each['name'], each['score'])
        return result

    def _getPlayerScoreString(playerId):
        stats = Stats._getPlayerStats(playerId, Round.getActiveId())
        if stats:
            return '{}:{}'.format(Player.getNameById(playerId), stats['score'])
        return ''

    def getTeamPlayerStatsStringByMobile(mobile):
        playerId = Player.getMobileOwnerId(mobile)
        return Stats._getPlayerScoreString(playerId) + Stats._getTeamScoreString()

#events

    def _eventTranslate(eventName):
        if eventName in game_config.event_type_translated:
            return game_config.event_type_translated[eventName]

    def getEventList(roundId, rows):
        events = Event.getEventListRaw(roundId, rows)
        if not events:
            return [{ 'event' : None }]
        eventList = []
        for ev in events:
            event, playerId, timestamp, teamVisible, message = ev
            thisEvent = {}
            thisEvent['time'] = timestamp.strftime(game_config.database_dateformat_hours_minutes)
            thisEvent['text1'] = { 'text' : Player.getNameById(playerId),
                                    'color' : Team.getColorById(Team.getPlayerTeamId(playerId, roundId))}
            thisEvent['text2'] = { 'text' : Stats._eventTranslate(EventType(event).name),
                                    'color' : 'FFFFFF'}
            if event == EventType.teamChat.value:
                thisEvent['visible'] = Team.getNameById(teamVisible)
                thisEvent['text3'] = { 'text' : message,
                                    'color' : Team.getColorById(teamVisible)}
            else:
                thisEvent['visible'] = 'All'
                player2Id = Event.getDidEventPair(event, timestamp)
                thisEvent['text3'] = { 'text' : Player.getNameById(player2Id),
                                    'color' : Team.getColorById(Team.getPlayerTeamId(player2Id, roundId))}
            eventList.append(thisEvent)
        return eventList

    def _storeEvents(events):
        if events:
            with open('events.json', 'w') as jsonFile:
                json.dump(events, jsonFile, indent = 4)

    def getRoundEvents():
        with open('events.json') as jsonFile:
            return json.load(jsonFile)

# print
    def printPlayersDetailed():
        Player.cur.execute("""SELECT player_data.player_id, player_data.player_name, player_data.player_mobile, player_data.player_web_hash, player_data.player_fleeing_code, code_list.spot_code, code_list.touch_code
            FROM player_data 
                JOIN code_list ON (player_data.player_code_id = code_list.code_id)
            """)
        rows = Player.cur.fetchall()
        print(" - ID MOB HASH  JAIL SPOT TOUCH   STATE  TEAM    NAME")
        for row in rows:
            (id, name, mobile, webHash, fleeingCode, spotCode, touchCode) = row
            team = Team.getNameById(Team.getPlayerTeamId(id, Round.getActiveId()))
            jailed = "jailed"
            if not Event.isPlayerJailed(id):
                jailed = "free  "
            print(" - ", id, mobile, webHash, fleeingCode, spotCode, touchCode, jailed, team, name)


# get
    def playersDetailed():
        Player.cur.execute("""SELECT player_data.player_id, player_data.player_name, player_data.player_mobile, player_data.player_web_hash, player_data.player_fleeing_code, code_list.spot_code, code_list.touch_code
            FROM player_data 
                LEFT JOIN code_list ON (player_data.player_code_id = code_list.code_id)
            """)
        rows = Player.cur.fetchall()
        players = []
        teamless = []
        for row in rows:
            player = []           
            (id, name, mobile, webHash, fleeingCode, spotCode, touchCode) = row
            team = Team.getNameById(Team.getPlayerTeamId(id, Round.getActiveId()))
            jailed = "jailed"
            if not Event.isPlayerJailed(id):
                jailed = "free  "
            print(" - ", id, mobile, webHash, fleeingCode, spotCode, touchCode, jailed, team, name)
            player.append(id)
            player.append(name)
            player.append(mobile)
            player.append(webHash)
            player.append(fleeingCode)
            player.append(spotCode)
            player.append(touchCode)
            player.append(jailed)
            player.append(team)
            if team == None:
                teamless.append(player)
            else:
                players.append(player)
        return players, teamless
