from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *


def processInput():
    userText = input("Enter command [Add player] [Team player] [Spot] [Web spot] [Flee jail] [Print] [teamChat]: \n")
    if 'f' in userText:
        jailCode = input("enter jail code: ")
        Action.fleePlayerWithCode(jailCode)
        Stats.printPlayersDetailed()
    elif 's' in userText:
        mobile = input("enter mobile: ")
        code = input("enter code: ")
        Action.handleSms(mobile, code)
        Stats.printPlayersDetailed()
    elif 'a' in userText:
        name = input("enter name: ")
        mobile = input("enter mobile: ")
        #email = input("enter email: ")
        Action.addPlayer(name, mobile, "")
        Stats.printPlayersDetailed()
    elif 'w' in userText:
        hash = input("enter player hash: ")
        code = input("enter code: ")
        Action.handleWeb(hash, code)
        Stats.printPlayersDetailed()
    elif 't' in userText:
        name = input("enter player name: ")
        team = input("enter team name: ")
        Action.addPlayerToTeam(name, team)
        Stats.printPlayersDetailed()
    elif 'p' in userText:
        Stats.printStats()
    elif 'c' in userText:
        name = input("enter name: ")
        message = input("enter text: ")
        playerId = Player._getIdByName(name)
        Action.sayToMyTeam(playerId, message)

