#!/usr/bin/env python3

#import game_config

import connect

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *





def main():
    connection = connect.connectDB()
    if not connection:
        return
    cursor = connection.cursor()

    Action.initAllOnce(cursor)

    Round.addTestRounds()
    Action.printPlayersDetailed()
    Action.addTestPlayers()
    Action.printPlayersDetailed()

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
# input validation
# multilingual support
# if new round starts - start it at event too Event.setRoundId
    # equality ! check types