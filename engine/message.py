from game_config import msgCellular, msgBase
from .round import Round
from .player import Player
import game_config
import time

class MessageChannel:
    message_list = []
    queue = None
    sms_count = 0

    def player_polled(playerId):
        playerId = str(playerId)
        for player in MessageChannel.message_list:
            if player['id'] == playerId:
                player['poll_time'] = time.time()
                return
        MessageChannel._add_player(playerId)

    def send_message(playerId, message):
        playerId = str(playerId)
        if MessageChannel._if_send_web(playerId):
            # last poll not so long ago, put message to queue to wait web request
            MessageChannel._add_message(playerId, message)
        else:
            smsdata = {
                'number': Player.getMobileById(playerId),
                'contents': message
                }
            if MessageChannel.queue:
                MessageChannel.queue.put(smsdata)
                MessageChannel.sms_count += 1
            print("SMS:", smsdata['number'], smsdata['contents'])

    def message_request(playerId):
        playerId = str(playerId)
        MessageChannel.player_polled(playerId)
        msg = MessageChannel._pop_message(playerId)
        if msg:
            print("Message:", msg['text'])
            return msg['text']

    def check_all():
        print("xx checkAll", MessageChannel.message_list)
        for player in MessageChannel.message_list:
            if time.time() - player['poll_time'] > 15:
                print("xx checkAll time passed")
                msg = MessageChannel._pop_message(player['id'])
                if not msg:
                    return
                player['last_sent'] = time.time()
                if MessageChannel.queue:
                    MessageChannel.queue.put(smsdata)
                    MessageChannel.sms_count += 1
                print("SMS:", smsdata['number'], smsdata['contents'])
                return


    def _if_send_web(playerId):
        for player in MessageChannel.message_list:
            if player['id'] == playerId:
                if time.time() - player['poll_time'] < 8: # 4:
                    return True
                return
        MessageChannel._add_player(playerId)


    def _add_message(playerId, message):
        for player in MessageChannel.message_list:
            if player['id'] == playerId:
                data = {}
                data['time'] = time.time()
                data['text'] = message
                player['messages'].append(data)
                return
        MessageChannel._add_player(playerId)
        MessageChannel._add_message(playerId, message)


    def _pop_message(playerId):
        for player in MessageChannel.message_list:
            if player['id'] == playerId:
                if player['messages']:
                    msg = player['messages'].pop(0)
                    if msg:
                        player['last_sent'] = time.time()
                        return msg

    def _add_player(playerId):
        data = {}
        data['id'] = playerId
        data['poll_time'] = time.time()
        data['last_sent'] = time.time() - 60.0
        data['messages'] = []
        MessageChannel.message_list.append(data)


class Sms:
    _statsCallback = None

    def setCallback(call):
        Sms._statsCallback = call

    def addUrl():
        return game_config.game_link_sms

    def send(mobile, data, sendStats = False, sendLink = False):
        if isinstance(mobile, str):
            if mobile.isdigit():
                if sendStats and Sms._statsCallback:
                    data += " " + Sms._statsCallback(mobile)
#                    data += " " + Stats.getTeamPlayerStatsString(Player.getMobileOwnerId(mobile))
                if sendLink:
                    data += " " + Sms.addUrl()
                MessageChannel.send_message(Player.getMobileOwnerId(mobile), data)
        else:
            print(" Errror! send sms", mobile, data)

    def notSignedUp(mobile):
        Sms.send(mobile, msgCellular['notSignedUp'].format(mobile), sendLink = True)

    def senderJailed(mobile, name, jailCode):
        Sms.send(mobile, msgCellular['senderJailed'].format(name, jailCode), sendStats = True, sendLink = True)

    def victimJailed(senderMobile, senderName, victimMobile, victimName, jailCode):
        Sms.send(victimMobile, msgCellular['victimJailedVictim'].format(victimName, senderName, jailCode), sendStats = True, sendLink = True)
        Sms.send(senderMobile, msgCellular['victimJailedSender'].format(senderName, victimName, victimName), sendStats = True, sendLink = True)

    def missed(mobile, name):
        Sms.send(mobile, msgCellular['missed'].format(name), sendStats = True, sendLink = True)

    def oldCode(mobile, nameSender, nameVictim):
        Sms.send(mobile, msgCellular['oldCode'].format(nameSender, nameVictim), sendStats = True, sendLink = True)

    def exposedSelf(mobile, name, jailCode):
        Sms.send(mobile, msgCellular['exposedSelf'].format(name, jailCode), sendStats = True, sendLink = True)

    def spotMate(senderMobile, senderName, victimMobile, victimName, jailCode):
        Sms.send(senderMobile, msgCellular['spotMateSender'].format(senderName, victimName), sendStats = True, sendLink = True)
        Sms.send(victimMobile, msgCellular['spotMateVictim'].format(victimName, jailCode), sendStats = True, sendLink = True)

    def spotted(senderMobile, senderName, victimMobile, victimName, jailCode):
        Sms.send(senderMobile, msgCellular['spottedSender'].format(senderName, victimName), sendStats = True, sendLink = True)
        Sms.send(victimMobile, msgCellular['spottedVictim'].format(victimName, jailCode), sendStats = True, sendLink = True)

    def touched(senderMobile, senderName, victimMobile, victimName, jailCode):
        Sms.send(senderMobile, msgCellular['touchedSender'].format(senderName, victimName), sendStats = True, sendLink = True)
        Sms.send(victimMobile, msgCellular['touchedVictim'].format(victimName, jailCode), sendStats = True, sendLink = True)

    def fleeingProtectionOver(mobile, name):
        Sms.send(mobile, msgCellular['fleeingProtectionOver'].format(name), sendLink = True)

    def noActiveRound(mobile, nextIn):
        Sms.send(mobile, msgCellular['noActiveRound'].format(nextIn))

    def roundStarted(mobile, roundName):
        Sms.send(mobile, msgCellular['roundStarted'].format(roundName), sendLink = True)

    def roundEnding(mobile, roundName, timeLeft):
        Sms.send(mobile, msgCellular['roundEnding'].format(roundName, timeLeft), sendStats = True)

    def roundEnded(mobile, roundName):
        Sms.send(mobile, msgCellular['roundEnded'].format(roundName), sendStats = True)

    def playerAdded(mobile, name, jailCode):
        Sms.send(mobile, msgCellular['playerAdded'].format(name, jailCode), sendLink = True)

    def alertGameMaster(message):
        Sms.send(game_config.game_master_mobile_number, message)


class BaseMsg:
    last_message = {}

    def get():
        if BaseMsg.last_message:
            if time.time() - BaseMsg.last_message['time'] > 15:
                BaseMsg.last_message = {}
        return BaseMsg.last_message

    def send(msg):
        print("  Base Msg:", msg)
        BaseMsg.last_message['text'] = msg
        BaseMsg.last_message['time'] = time.time()

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
