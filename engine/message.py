from game_config import msgCellular, msgBase

class Sms:
    _count = 0
    _statsCallback = None

    def setCallback(call):
        Sms._statsCallback = call

    def send(mobile, data, sendStats = False):
        if isinstance(mobile, str):
            if mobile.isdigit():
                if sendStats and Sms._statsCallback:
                    data += " " + Sms._statsCallback(mobile)
#                    data += " " + Stats.getTeamPlayerStatsString(Player.getMobileOwnerId(mobile))
                print("     SMS:", mobile, data)
# TODO placeholder to true SMS send function
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
# TODO placeholder to true base message send function
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
