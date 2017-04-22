from .code import Code
from .event import Event
from .player import Player
from .round import Round
from .team import Team

import time

class Action:

    def handleCode(mobile, code):
        senderId = Player.getIdByMobile(mobile)
        victimId = Code.getOwnerId(code)
        senderAlive = Event.isPlayerAlive(senderId)
        victimAlive = Event.isPlayerAlive(victimId)
        if not senderId:
            print("this player has not been signed up for the game", mobile)
            # send back sms "come to the base and sign up"
            #Event.addStrangeSms(mobile, code)
            return
        if not senderAlive:
            print("sender not alive")
            # sms: teleport to the base.
            return
        if not victimId:
            print("missed hit")
            Event.addMissedHit(senderId, code)
            return
        if not victimAlive:
            print("victim not alive")
            # sms victim: teleport to the base
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

    def spawnPlayer(playerId, respawnCode):
        if Player.checkRespawnCode(playerId, respawnCode):
            Player.regenerateRespawnCode(playerId)
            Event.addSpawn(playerId)
        else:
            print("sorry, this respawn code did not match!")

#    def headshotVictim(victimId):

    def addPlayer(name, mobile, email):
        newPlayerId = Player.add(name, mobile, email)
#        Code.generateNewShotCode(newPlayerId)

    def respawn(playerId):
        if not Event.isPlayerAlive(playerId):
            Player.regenerateRespawnCode(playerId)
            Event.addSpawn(playerId)
            print(playerId, "respawned!")
        else:
            print(playerId, "alive, didnt respawn!")

    def addTestAction():
        Code.generateNewShotCode(1)
        Code.generateNewShotCode(2)
        Code.generateNewShotCode(3)
        Code.generateNewShotCode(4)
        Action.respawn(1)
        Action.respawn(2)
        Action.respawn(3)
        Action.respawn(4)


        print("1-1")
        Action.handleCode(Player.getMobileById(1), Code.getCodeById(Code.getCodeIdByPlayerId(1)))
        print(" alive", Event.isPlayerAlive(1))
        Action.respawn(1)
        time.sleep(2)
        print("4-1")
        Action.handleCode(Player.getMobileById(4), Code.getCodeById(Code.getCodeIdByPlayerId(1)))
        print(" alive", Event.isPlayerAlive(1))
        Action.respawn(1)
        time.sleep(2)
        print("4-1")
        Action.handleCode(Player.getMobileById(4), Code.getCodeById(Code.getCodeIdByPlayerId(1)))
        print(" alive", Event.isPlayerAlive(1))
        Action.respawn(4)
        time.sleep(2)
        print("1-2")
        Action.handleCode(Player.getMobileById(1), Code.getCodeById(Code.getCodeIdByPlayerId(2)))
        print(" alive", Event.isPlayerAlive(1))
        Action.respawn(2)
        time.sleep(2)
        print("1-3")
        Action.handleCode(Player.getMobileById(1), Code.getCodeById(Code.getCodeIdByPlayerId(3)))
        print(" alive", Event.isPlayerAlive(1))
        Action.respawn(1)
        time.sleep(2)
        Action.handleCode(Player.getMobileById(1), Code.getCodeById(Code.getCodeIdByPlayerId(4)))
        print(" alive", Event.isPlayerAlive(1))
#        time.sleep()
#        Action.handleCode('3253234', Code.getCodeById(Code.getCodeIdByPlayerId(4)))
#        Action.handleCode(Player.getMobileById(1), 4745)
