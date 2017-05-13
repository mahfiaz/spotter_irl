#!/usr/bin/env python3

#import game_config

import connect

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *


def processInput():
    userText = input("Enter command [Add player] [Team player] [Spot] [Web spot] [Flee jail] [Print]: ")
    if 'f' in userText:
        jailCode = input("enter jail code: ")
        Action.fleePlayerWithCode(jailCode)
        Action.printPlayersDetailed()
    if 's' in userText:
        mobile = input("enter mobile: ")
        code = input("enter code: ")
        Action.handleSms(mobile, code)
        Action.printPlayersDetailed()
    if 'a' in userText:
        name = input("enter name: ")
        mobile = input("enter mobile: ")
        email = input("enter email: ")
        Action.addPlayer(name, mobile, email)
        Action.printPlayersDetailed()
    if 'w' in userText:
        hash = input("enter player hash: ")
        code = input("enter code: ")
        Action.handleWeb(hash, code)
        Action.printPlayersDetailed()
    if 't' in userText:
        name = input("enter player name: ")
        team = input("enter team name: ")
        Action.addPlayerToTeam(name, team)
        Action.printPlayersDetailed()
    if 'p' in userText:
        Action.printStats()


def main():
    connection = connect.connectDB()
    if not connection:
        return
    cursor = connection.cursor()

    Action.initAllConnect(cursor)

    Round.updateActiveId()
    Action.updateStats()
    Action.printPlayersDetailed()

#    Action.addPlayersToTeams()

    while True:
        processInput()



if __name__ == "__main__":
    main()

# TODO
    # interfacing with web
    # input validation
# if new round starts - start it at event too Event.setRoundId
    # equality ! check types