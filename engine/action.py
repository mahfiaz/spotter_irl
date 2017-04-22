from .code import Code
from .event import Event
from .player import Player
from .round import Round
from .team import Team

class Action:

    def handleCode(mobile, code):
        senderId = Player.getIdByMobile(mobile)
        victimId = Code.getOwnerId(code)
        if not senderId:
            print("this player has not been signed up for the game", mobile)
            # send back sms "come to the base and sign up"
            #Event.addStrangeSms(mobile, code)
            return
        if not victimId:
            print("missed hit")
            Event.addMissedHit(senderId, code)
            return
        if senderId == victimId:
            print("suicide")
            Event.addSuicide(victimId)
            Action.shotVictim(senderId)
            # suicide sms
            return
        if Team.getPlayerTeamId(senderId) == Team.getPlayerTeamId(victimId):
            print("teammate")
            Event.addHitTeamMate(senderId, victimId)
            Action.shotVictim(victimId)
            # friendly fire warning sms
            return
        else:
            print("normal hit")
            Event.addHit(senderId, victimId)
            Action.shotVictim(victimId)
            # sms: successful shot

    def shotVictim(victimId):
#        Code.generateNewShotCode(victimId)
        Team.updateStats()

#    def spawnPlayer()

#    def headshotVictim(victimId):

    def addPlayer(name, mobile, email):
        newPlayerId = Player.add(name, mobile, email)
#        Code.generateNewShotCode(newPlayerId)

    def addTestAction():
        Code.generateNewShotCode(1)
        Code.generateNewShotCode(2)
        Code.generateNewShotCode(3)
        Code.generateNewShotCode(4)

        Action.handleCode(Player.getMobileById(1), Code.getCodeById(Code.getCodeIdByPlayerId(1)))
        Action.handleCode(Player.getMobileById(4), Code.getCodeById(Code.getCodeIdByPlayerId(1)))
        Action.handleCode(Player.getMobileById(4), Code.getCodeById(Code.getCodeIdByPlayerId(1)))
        Action.handleCode(Player.getMobileById(1), Code.getCodeById(Code.getCodeIdByPlayerId(2)))
        Action.handleCode(Player.getMobileById(1), Code.getCodeById(Code.getCodeIdByPlayerId(3)))
        Action.handleCode(Player.getMobileById(1), Code.getCodeById(Code.getCodeIdByPlayerId(4)))
        Action.handleCode('3253234', Code.getCodeById(Code.getCodeIdByPlayerId(4)))
        Action.handleCode(Player.getMobileById(1), 4745)
