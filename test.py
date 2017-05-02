#!/usr/bin/env python3

import connect

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *

teamName1 = "Sinised"
teamName2 = "Punased"


def addTestRoundsShort():
    time.strftime(dateformat)
    time1 = format(datetime.datetime.now() + datetime.timedelta(seconds = -20), dateformat)
    time2 = format(datetime.datetime.now() + datetime.timedelta(seconds = -10), dateformat)
    time3 = format(datetime.datetime.now() + datetime.timedelta(seconds = -2), dateformat)
    time4 = format(datetime.datetime.now() + datetime.timedelta(seconds = 5), dateformat)
    time5 = format(datetime.datetime.now() + datetime.timedelta(seconds = 10), dateformat)
    time6 = format(datetime.datetime.now() + datetime.timedelta(seconds = 15), dateformat)
    time7 = format(datetime.datetime.now() + datetime.timedelta(seconds = 15), dateformat)

    Round.add("first", time1, time2)
    Round.add("second", time2, time3)
    Round.add("third", time3, time4)
    Round.add("fourth", time2, time4)
    Round.add("fifth", time5, time6)
    Round.add("sixth", time6, time7)
    Round.updateActiveId()
    assert Round.getActiveId() == 3

def addTestRoundsNormal():
    time.strftime(dateformat)
    time3 = format(datetime.datetime.now() + datetime.timedelta(seconds = -2), dateformat)
    time4 = format(datetime.datetime.now() + datetime.timedelta(seconds = 10 * 60), dateformat)

    Round.add("third", time3, time4)
    Round.updateActiveId()


def addTestTeams():
    teamCount = len(Team.getTeamsIdList(Round.getActiveId()))
    # shouldnt add, because roundId invalid
    Team.add(teamName1, roundId = 0)
    assert len(Team.getTeamsIdList(Round.getActiveId())) == teamCount

    # shouldnt add, because roundId invalid
    Team.add(teamName2, roundId = 0)
    assert len(Team.getTeamsIdList(Round.getActiveId())) == teamCount

    Team.add(teamName1, roundId = Round.getActiveId())
    assert len(Team.getTeamsIdList(Round.getActiveId())) == teamCount + 1

    Team.add(teamName2, roundId = Round.getActiveId())
    assert len(Team.getTeamsIdList(Round.getActiveId())) == teamCount + 2

    # should not add, because name is not unique
    Team.add(teamName1, roundId = Round.getActiveId())
    assert len(Team.getTeamsIdList(Round.getActiveId())) == teamCount + 2


def addTestPlayers():
    dataDict = ({"name":"Ets2", "mobile":"111", "email":"ets@gail.cm"},
            {"name":"Volts", "mobile":"222", "email":"Volts@gail.cm"},
            {"name":"KalleLalle", "mobile":"333", "email":"Kdfi@gail.cm"},
            {"name":"Miku", "mobile":"444", "email":"Vofdss@gail.cm"},
            {"name":"Jooksik", "mobile":"555", "email":"gjajdli@gail.cm"},
            {"name":"Veiks", "mobile":"888", "email":"KA3l3li@gail.cm"})
    for each in dataDict:
        Action.addPlayer(each['name'], each['mobile'], each['email'])
    assert len(Player.getAllPlayerIds()) == 6

    Action.addPlayer(dataDict[3]['name'], '453', 'klwer@gm.com')
    assert len(Player.getAllPlayerIds()) == 6

    Action.addPlayer('Uuno', dataDict[3]['mobile'], 'klwer@gm.com')
    assert len(Player.getAllPlayerIds()) == 6

    Action.addPlayer('Uuno', '2346', dataDict[3]['email'])
    assert len(Player.getAllPlayerIds()) == 6

    Action.printPlayersDetailed()


def addPlayersToTeams():
    players = Player.getAllPlayerIds()
    for pl1, pl2 in zip(players[0::2], players[1::2]):
        Team.addPlayer(pl1, Team._getIdByName(teamName1, Round.getActiveId()))
        Team.addPlayer(pl2, Team._getIdByName(teamName2, Round.getActiveId()))

def fleeAllPlayers():
    for playerId in Player.getAllPlayerIds():
        Action.fleePlayerWithCode(Player.getFleeingCode(playerId))
    Action.printPlayersDetailed()

def addTestAction():
    # not registered user test
    Action.handleCodeValidate("4678", Code.getSpotCodeByPlayerId(1))


    print("1-1")
    disloyality1 = Event.getPlayerDisloyalityCount(1, Round.getActiveId())
    Action.handleCodeValidate(Player.getMobileById(1), Code.getSpotCodeByPlayerId(1))
    assert Event.getPlayerDisloyalityCount(1, Round.getActiveId()) == disloyality1 + 1
#    Action.fleePlayerWithCode(Player.getFleeingCode(4))
    Action.printPlayersDetailed()
    time.sleep(0.1)

    print("4-1")
    spotsTotal4 = Event.getPlayerSpotCount(4, Round.getActiveId())
    Action.handleCodeValidate(Player.getMobileById(4), Code.getSpotCodeByPlayerId(1))
    assert Event.getPlayerSpotCount(4, Round.getActiveId()) == spotsTotal4
    Action.printPlayersDetailed()
    Action.fleePlayerWithCode(Player.getFleeingCode(1))
    time.sleep(0.1)

    print("4-1")
    spotsTotal4 = Event.getPlayerSpotCount(4, Round.getActiveId())
    jailed1 = Event.getPlayerJailedCount(1, Round.getActiveId())
    Action.handleCodeValidate(Player.getMobileById(4), Code.getSpotCodeByPlayerId(1))
    assert Event.getPlayerSpotCount(4, Round.getActiveId()) == spotsTotal4 + 1
    assert Event.getPlayerJailedCount(1, Round.getActiveId()) == jailed1 + 1
    Action.printPlayersDetailed()
    Action.fleePlayerWithCode(Player.getFleeingCode(4))
    time.sleep(0.1)

    print("1-3 teammate")
    Action.fleePlayerWithCode(Player.getFleeingCode(1))
    spots1 = Event.getPlayerSpotCount(1, Round.getActiveId())
    disloyality1 = Event.getPlayerDisloyalityCount(1, Round.getActiveId())
    Action.handleCodeValidate(Player.getMobileById(1), Code.getSpotCodeByPlayerId(3))
    assert Event.getPlayerSpotCount(1, Round.getActiveId()) == spots1
    assert Event.getPlayerDisloyalityCount(1, Round.getActiveId()) == disloyality1 + 1
    Action.fleePlayerWithCode(Player.getFleeingCode(1))

    fleeAllPlayers()
    time.sleep(0.1)

    print("1-H4", Code.getTouchCodeByPlayerId(4))
    touchTotal1 = Event.getPlayerTouchCount(1, Round.getActiveId())
    Action.handleCodeValidate(Player.getMobileById(1), Code.getTouchCodeByPlayerId(4))
    assert Event.getPlayerTouchCount(1, Round.getActiveId()) == touchTotal1 + 1
    Action.fleePlayerWithCode(Player.getFleeingCode(1))
    Action.printPlayersDetailed()
    time.sleep(0.1)

def processInput():
    userText = input("Enter command [a] [s] [f] [q]: ")
    if 'f' in userText:
        jailCode = input("enter jail code: ")
        Action.fleePlayerWithCode(jailCode)
        Action.printPlayersDetailed()
    if 's' in userText:
        mobile = input("enter mobile: ")
        code = input("enter code: ")
        Action.handleCodeValidate(mobile, code)
        Action.printPlayersDetailed()
    if 'a' in userText:
        name = input("enter name: ")
        mobile = input("enter mobile: ")
        email = input("enter email: ")
        Action.addPlayer(name, mobile, email)
        Action.printPlayersDetailed()
    if 'q' in userText:
        return True

def testWithInput():
    connection = connect.connectDB()
    if not connection:
        return
    cursor = connection.cursor()

    Action.initAllOnce(cursor)
#    addTestRoundsShort()
    addTestRoundsNormal()
    Action.addTeams(Round.getActiveId())
    addTestPlayers()
    addPlayersToTeams()
    fleeAllPlayers()
    Action.updateStats()
    stop = False
    while not stop:
        stop = processInput()
    return

def quickTest():
    connection = connect.connectDB()
    if not connection:
        return
    cursor = connection.cursor()

    Action.initAllOnce(cursor)
    addTestRoundsShort()
    addTestTeams()
    addTestPlayers()
    addPlayersToTeams()
    fleeAllPlayers()
    addTestAction()

if __name__ == "__main__":
#    testWithInput()
    quickTest()
