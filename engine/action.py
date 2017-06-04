from .code import Code
from .event import Event, EventType
from .player import Player
from .round import Round
from .team import Team
from .message import Sms, BaseMsg, MessageChannel
import game_config

import json
import time
import random
import re
import pprint
from threading import Timer


class Game:
    started = False

    def __init__(self, config, cursor):
        self.config = config
        self.cursor = cursor
        self.A = Site(self, 'A')
        self.B = Site(self, 'B')
        self.C = Site(self, 'C')
        self.CT = Site(self, 'CT')
        self.TR = Site(self, 'TR')
        self.sites = {'A': self.A, 'B': self.B, 'C': self.C, 'CT': self.CT, 'TR': self.TR}

        self.teams = {}
        self.teams['CT'] = TeamNew(self, 'CT')
        self.teams['TR'] = TeamNew(self, 'TR')
        
        self.reset()

    def reset(self):
        self.sendall('reset')

    def start(self):
        self.started = True
        self.sendall('started')

    def planted(self, origin):
        self.started = True
        self.sendall('planted', {'origin': origin})

    def ended(self, origin, winner):
        self.started = True
        self.sendall('ended', {'origin': origin, 'winner': winner})

    def sendall(self, message, data = {}):
        for name in self.sites:
            site = self.sites[name]
            site.events.append([message, data])

class TeamNew:
    ready = False

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def setReady(self, value):
        self.ready = value
        if self.parent.teams['CT'].ready and \
            self.parent.teams['TR'].ready:
            self.parent.start()


class Site:
    locked = True
    code = None
    shortcode = None

    starting = False

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.lock()
        self.events = []

    def lock(self):
        self.locked = True
        self.code = self.generate_code(7)
        self.shortcode = self.generate_code(3)
        return (self.code, self.shortcode)

    def unlock(self, code):
        if str(code) == str(self.code) \
            or str(code) == str(self.shortcode):
            self.locked = False
            return 'Site %s unlocked' % self.name
        else:
            return 'Code not correct'

    def generate_code(self, length):
        min_num = 10 ** (length - 1) + 1
        max_num = 10 ** length - 1
        # Ensure it's odd for A and even for B
        while True:
            code = random.randint(min_num, max_num)
            if self.name == 'A' and (code % 2) == 1:
                break
            elif self.name == 'B' and (code % 2) == 0:
                break
            elif self.name not in ['A', 'B']:
                # Don't care
                break
        return code


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

    def initAllConnect(cursor, sms_queue, printer_queue):
        Round.initConnect(cursor)
        Player.initConnect(cursor)
        Code.initConnect(cursor)
        Team.initConnect(cursor)
        Event.initConnect(cursor)
#        Round.setCallbacks(roundStarted = Action._roundStartedCall, roundEnding = Action._roundEndingCall, roundEnded = Action._roundEndedCall)
        Stats.updateStats()
        MessageChannel.queue = sms_queue
        Sms.setCallback(Stats.getTeamPlayerStatsStringByMobile)
        Action.printer_queue = printer_queue
        Action.checked_last = 0

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
            Event.addFlee(newPlayerId)
            return newPlayerId
        else:
            BaseMsg.playerNotUnique(name, mobile, email)

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
            # auto flee
            fleecode = Player.getFleeingCode(playerId)
            Action.fleePlayerWithCode(str(fleecode))
            Event.addPlayerToTeam(playerId)
            Event.addFlee(playerId)
        else:
            print("Error when adding player to team")
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
        return Action._handleCode(senderId, code, byMobile = False)

    def _handleCode(senderId, code, byMobile):
        mobile = Player.getMobileById(senderId)
        senderJailed = Event.isPlayerJailed(senderId)
        senderName = Player.getNameById(senderId)
        if not senderId:
            Event.addObscureMessage(senderId, code)
            if byMobile and mobile:
                Sms.notSignedUp(mobile)
            return False
        if not Round.updateActiveId() or not code:
            Event.addObscureMessage(senderId, code)
            if byMobile:
                Sms.noActiveRound(mobile, Round._getStartTimeOfNext())
            return False
        if not Team.getPlayerTeamId(senderId, Round.getActiveId()):
#            Sms.alertGameMaster(senderName + " not added to any team! Please add!")
            return False
        code = int(code)
        if senderJailed:
            Sms.senderJailed(mobile, senderName, Player.getFleeingCode(senderId))
            # store event too
            return "Sa ei saa teisi hittida, kui oled ise hititud, pöördu tagasi baasi"
        victimId, codeValid = Code.getVictimIdByCode(code)
        if not victimId:
            # first add event, then update stats and then send sms with updated stats
            Event.addFailedSpot(senderId, code)
            Stats.updateStats()
            Sms.missed(mobile, Player.getNameById(senderId))
            return "Tundub, et sisestasid vale koodi"
        if not Team.getPlayerTeamId(victimId, Round.getActiveId()):
            Sms.alertGameMaster(Player.getNameById(victimId) + " not added to any team! Please add!")
            return False
        victimJailed = Event.isPlayerJailed(victimId)
        victimName = Player.getNameById(victimId)
        victimMobile = Player.getMobileById(victimId)
        if not codeValid:
            Event.addWasAimedWithOldCode(victimId, code)
            Sms.oldCode(mobile, senderName, victimName)
            return False
        if victimJailed:
            Sms.victimJailed(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
            return "Oleksid muidu hittinud, aga ta oli juba pihta saanud"
        assert type(senderId) == type(victimId)
        if senderId == victimId:
            Event.addExposeSelf(victimId)
            Stats.updateStats()
            Sms.exposedSelf(mobile, senderName, Player.getFleeingCode(senderId))
            return "Hittisid ennast, järgmine kord ole hoolikam, selleks korraks on mäng sinu jaoks läbi, pöördu tagasi baasi"
        if Team.getPlayerTeamId(senderId, Round.getActiveId()) == Team.getPlayerTeamId(victimId, Round.getActiveId()):
            Event.addSpotMate(senderId, victimId)
            Stats.updateStats()
            Sms.spotMate(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
            return "Hittisid oma meeskonna kaaslast"
        else:
            if Code._isValidSpotCodeFormat(code):
                Event.addSpot(senderId, victimId)
                Stats.updateStats()
                Sms.spotted(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
                return "Hea töö, hittisid vastast"
            elif Code._isValidTouchCodeFormat(code):
                Event.addTouch(senderId, victimId)
                Stats.updateStats()
                Sms.touched(mobile, senderName, victimMobile, victimName, Player.getFleeingCode(victimId))
                return "Erakordne õnn või häkk, aga punkte selle hiti eest ei jagata"

# message spool
    # player's browser requests for user messages. if these requests come frequently (<4s), any Sms-message is queued and served one-by-one on by this function.
    def browserRequestsMessages(hash):
        pollerId = Player.getIdByHash(hash)
        if pollerId:
            return MessageChannel.message_request(pollerId)

    # if there is no browserRequestsMessages() in 15s, messages_timeout_check() send the queued message as sms.
    def messages_timeout_check():
        if time.time() - Action.checked_last > 1.0:
            MessageChannel.check_all()
            Action.checked_last = time.time()

    # base.html should poll this to get messages for jail fleeing players. returns same message until it expires (15 sec) or it is overwritten by new one.
    def base_msg_get():
        return BaseMsg.get()

# teamchat
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
        print("Teamchat: ", Player.getNameById(playerId), "said ", message)
        Event.addChatMessage(playerId, teamId, message)
        Stats.updateEvents()

    def masterAnnounces(message):
        Action.sayToMyTeam(Player.getMasterId(), message)

# flee
    def fleePlayerWithCode(fleeingCode):
        code = Action._codeValidate(fleeingCode)
        if not code:
            print("Fleeing: Tried wrong code:", code)
            return
        if not Round.getActiveId():
            print("Warning. No active round. Fleeing not possible. Code:" ,fleeingCode)
            return
        playerId = Player.checkFleeingCode(code)
        if playerId:
            if not Team.getPlayerTeamId(playerId, Round.getActiveId()):
                team_name = Action.suggestedTeam()
                player_name = Player.getNameById(playerId)
                Action.addPlayerToTeam(player_name, team_name)
                print("Player %s automatically assigned to team %s" % (playerId, team_name))
            Action._flee(playerId)
            Stats.updateStats()
            # Print label
            Action.printer_queue.put(Action.prepareDataForPrinter(playerId))
        else:
            print("Fleeing code not matched to a player ID. Code:", code)
            BaseMsg.fleeingCodeMismatch()

    def suggestedTeam():
        """Assign to either smaller or to a random team."""
        round_id = Round.getActiveId()
        team_ids = Team.getTeamsIdList(round_id)
        team_members = []
        for team_id in team_ids:
            player_list = Team.getTeamPlayerIdList(team_id)
            team_members.append(len(player_list))
        if team_members[0] == team_members[1]:
            # Random team
            team_id = random.choice(team_ids)
        elif team_members[0] > team_members[1]:
            team_id = team_ids[1]
        else:
            team_id = team_ids[0]
        return Team.getNameById(team_id)

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
#                timer = Timer(game_config.player_fleeingProtectionTime, Action._fleeTimerCall, (Player.getMobileById(playerId), Player.getNameById(playerId),))
#                timer.daemon=True
#                timer.start()
#                BaseMsg.fledSuccessful(Player.getNameById(playerId), round(game_config.player_fleeingProtectionTime / 60, 1))
                return playerId
            else:
#                BaseMsg.cantFleeFromLiberty(Player.getNameById(playerId))
                return False

    def _unbanAllChats():
        for playerId in Player.getAllPlayerIds():
            Player.unbanChat(playerId)

# round calls
    def _roundStartedCall(mobileNameList, roundName):
        Action.masterAnnounces("Lahing " + roundName + " algas. CT meeskond väljub.")

        timer = Timer(30 - 5, Action._team_tr_starting_in_callback, 5)
        timer.daemon=True
        timer.start()

        timer = Timer(30, Action._team_tr_ready_callback, 0)
        timer.daemon=True
        timer.start()

#        BaseMsg.roundStarted()
#        for (mobile, name) in mobileNameList:
#            Sms.roundStarted(mobile, roundName)
#        for id in Player.getAllPlayerIds():
#            Player.unbanChat(id)

    def _team_tr_starting_in_callback(timeleft):
        Action.masterAnnounces("TR stardib " + str(timeleft) + " sek pärast.")

    def _team_tr_ready_callback(timeleft):
        Action.masterAnnounces("TR meeskond startis.")

    def _roundEndingCall(mobileNameList, roundName, left):
        Action.masterAnnounces("Lahing " + roundName + " lõpeb " + str(left) + " min pärast. Tule autasustamisele baasi.")
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
            'smsCount'          : MessageChannel.sms_count,
            'teams'             : allTeams,
            'teamlessPlayers'   : Stats._getTeamplessPlayerStats(roundId) }
        return roundStats

    def _storeStats(stats):
        if stats:
            with open('www/stats.json', 'w') as jsonFile:
                json.dump(stats, jsonFile, indent=4)

    def getRoundStats():
        with open('www/stats.json') as jsonFile:
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
            with open('www/events.json', 'w') as jsonFile:
                json.dump(events, jsonFile, indent = 4)

    def getRoundEvents():
        with open('www/events.json') as jsonFile:
            return json.load(jsonFile)

# print
    def printPlayersDetailed():
        Player.cur.execute("""SELECT player.pid, player_data.name, player_data.mobile, player_data.cookie, player_data.fleeing_code, codes.spot_code, code_list.touch_code
            FROM players
                JOIN codes ON (player.cid = code_list.code_id)
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
        Player.cur.execute("""SELECT player.pid, player_data.name, player_data.mobile, player_data.cookie, player_data.fleeing_code, codes.spot_code, code_list.touch_code
            FROM players
                LEFT JOIN codes ON (player.cid = code_list.code_id)
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
