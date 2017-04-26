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
        victimId = Code.getVictimIdByCode(code)
        senderJailed = Event.isPlayerJailed(senderId)
        victimJailed = Event.isPlayerJailed(victimId)
        if not senderId:
            print("this player has not been signed up for the game", mobile)
            # send back sms "come to the base and sign up"
            #Event.addStrangeSms(mobile, code)
            return
        if senderJailed:
            print(senderId, " jailed, could not spot anybody")
            # sms: teleport to the base.
            return
        if not victimId:
            print(senderId, "had a missed hit")
            Event.addFailedSpot(senderId, code)
            return
        if victimJailed:
            print(victimId, "victim jailed.", senderId, " is using old information")
            # sms victim: teleport to the base
            return
        if senderId == victimId:
            print(senderId, "exposed self to authorities")
            Event.addExposeSelf(victimId)
            Team.updateStats()
            # suicide sms
            return
        if Team.getPlayerTeamId(senderId) == Team.getPlayerTeamId(victimId):
            print(senderId, " did hit teammate ", victimId)
            Event.addSpotMate(senderId, victimId)
            Team.updateStats()
            # friendly fire warning sms
            return
        else:
            if Code._isValidSpotCodeFormat(code):
                print(senderId, " spotted ", victimId)
                Event.addSpot(senderId, victimId)
                # sms: successful spotting
            elif Code._isValidTouchCodeFormat(code):
                print(senderId, " touched ", victimId)
                Event.addTouch(senderId, victimId)
                # sms: successful touch
            Team.updateStats()

    def addPlayer(name, mobile, email):
        newPlayerId = Player.add(name, mobile, email)
        Event.addPlayer(newPlayerId)
        return newPlayerId
#        Code.generateNewCodes(newPlayerId)

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

    def addTestPlayers():
        dataDict = ({"name":"Ets2", "mobile":"111", "email":"ets@gail.cm"},
                {"name":"Vollts", "mobile":"222", "email":"Volts@gail.cm"},
                {"name":"KalleLalle", "mobile":"333", "email":"KAlli@gail.cm"},
                {"name":"lililii", "mobile":"444", "email":"KA3l3li@gail.cm"})
        for each in dataDict:
            Action.addPlayer(each['name'], each['mobile'], each['email'])
        Player.printDetailed()

    def addTestAction():
        for playerId in Player.getAllPlayerIds():
            Code.generateNewCodes(playerId)
#            Action._flee(playerId)
        Player.printDetailed()
        Action.addTestAction2()

    def addTestAction2():
        Player.printDetailed()
        Action.fleePlayerWithCode(1, Player.getFleeingCode(1))

        print("1-1")
        Action.handleCode(Player.getMobileById(1), Code.getSpotCodeByPlayerId(1))

        Player.printDetailed()

        time.sleep(1)
        print("4-1")
        Action.handleCode(Player.getMobileById(4), Code.getSpotCodeByPlayerId(1))
        Player.printDetailed()
        Action.fleePlayerWithCode(1, Player.getFleeingCode(1))
        Player.printDetailed()

        time.sleep(1)

        print("4-1")
        Action.handleCode(Player.getMobileById(4), Code.getSpotCodeByPlayerId(1))
        Player.printDetailed()
        Action.fleePlayerWithCode(4, Player.getFleeingCode(4))
        Player.printDetailed()

        time.sleep(1)
        print("1-2")
        Action.handleCode(Player.getMobileById(1), Code.getSpotCodeByPlayerId(2))
        Player.printDetailed()
        Action.fleePlayerWithCode(2, Player.getFleeingCode(2))
        Action.fleePlayerWithCode(2, Player.getFleeingCode(1))
        Player.printDetailed()
        time.sleep(1)

        Action.fleePlayerWithCode(3, Player.getFleeingCode(3))
        print("1-H3", Code.getTouchCodeByPlayerId(3))
        Action.handleCode(Player.getMobileById(1), Code.getTouchCodeByPlayerId(3))
        Player.printDetailed()
        Action.fleePlayerWithCode(1, Player.getFleeingCode(1))
        Player.printDetailed()
        time.sleep(1)

        Action.handleCode(Player.getMobileById(1), Code.getSpotCodeByPlayerId(4))
        Player.printDetailed()

#        time.sleep()
#        Action.handleCode('3253234', Code._getSpotCodeById(Code._getCodeIdByPlayerId(4)))
#        Action.handleCode(Player.getMobileById(1), 4745)
