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
    userText = input("Enter command [spot] [flee]: ")
    if 'flee' in userText:
        id = input("enter id: ")
        if Player.getNameById(id):
            Action._flee(id)
            Player.printDetailed()
    if 'spot' in userText:
        mobile = input("enter mobile: ")
        code = input("enter code: ")
        Action.handleCode(mobile, code)
        Player.printDetailed()

def main():
    connection = connect.connectDB()
    if not connection:
        return
    cursor = connection.cursor()

    Action.initAllOnce(cursor)

    Round.addTestRounds()
    Player.printDetailed()
    Action.addTestPlayers()
    Player.printDetailed()

    Round.print()
    print("round active", Round.isActive())

    Action.addTestTeams()
    Action.addPlayersToTeams()

#    Event.addTestEvents()

    Action.addTestAction()

    print(Action._calcAllStats(Round.getActiveId()))
    #Action.addTestAction2()

#    while True:
#        processInput()



if __name__ == "__main__":
    main()

#TODO
# private members _underscore
# if new round starts - start it at event too Event.setRoundId
# return variables some are duples (var,)
# event analysis on rounds
#equality ! check types