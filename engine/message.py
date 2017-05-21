from game_config import msgCellular, msgBase
from .round import Round
import game_config


class Sms:
    _count = 0
    _statsCallback = None
    queue = None

    def setQueue(queue):
        Sms.queue = queue

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
                    data += " # " + Sms.addUrl()
                print("     SMS:", mobile, data)

# TODO placeholder to true SMS send function
                smsdata = {
                    'number': mobile,
                    'contents': data
                    }
                if Sms.queue:
                    Sms.queue.put(smsdata)
                    Sms._count += 1
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

    def send(msg):
# TODO placeholder to true base message send function
        print("        Base Msg:", msg)
        #Sms.queue.put(['', msg])

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
