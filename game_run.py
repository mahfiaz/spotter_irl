#!/usr/bin/env python3

#import game_config

from queue import Queue
from threading import Thread

import connect
import queue

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *

from smsserver import send_sms, receive_sms

def processInput():
    userText = input("Enter command [Add player] [Team player] [Spot] [Web spot] [Flee jail] [Print] [teamChat] [BanChat] [MasterAnnounce]: \n")
    if 'f' in userText:
        jailCode = input("enter jail code: ")
        Action.fleePlayerWithCode(jailCode)
        Stats.printPlayersDetailed()
    if 's' in userText:
        mobile = input("enter mobile: ")
        code = input("enter code: ")
        Action.handleSms(mobile, code)
        Stats.printPlayersDetailed()
    if 'a' in userText:
        name = input("enter name: ")
        mobile = input("enter mobile: ")
        email = input("enter email: ")
        Action.addPlayer(name, mobile, email)
        Stats.printPlayersDetailed()
    if 'w' in userText:
        hash = input("enter player hash: ")
        code = input("enter code: ")
        Action.handleWeb(hash, code)
        Stats.printPlayersDetailed()
    if 't' in userText:
        name = input("enter player name: ")
        team = input("enter team name: ")
        Action.addPlayerToTeam(name, team)
        Stats.printPlayersDetailed()
    if 'p' in userText:
        Stats.printStats()
    if 'c' in userText:
        name = input("enter name: ")
        message = input("enter text: ")
        playerId = Player._getIdByName(name)
        Action.sayToMyTeam(playerId, message)
    if 'b' in userText:
        name = input("enter name: ")
        ban = input("ban? y/n: ")
        playerId = Player._getIdByName(name)
        if 'y' in ban:
            Player.banChat(playerId)
        if 'n' in ban:
            Player.unbanChat(playerId)
    if 'm' in userText:
        message = input("enter master message: ")
        Action.masterAnnounces(message)


def main():
    connection = connect.connectDB()
    if not connection:
        print("Could not connect to database")
        return
    cursor = connection.cursor()

    # Queues 
    sms_queue = queue.Queue()
    printer_queue = queue.Queue()

    Action.initAllConnect(cursor, sms_queue, printer_queue)

    Round.updateActiveId()
    Stats.updateStats()
    Stats.printPlayersDetailed()

#    Action.addPlayersToTeams()

    # Queue for incoming events from web server and incoming SMSes
    incoming_events = Queue()

    # Start SMS receiving thread
    # incoming SMSes will be parsed to events
#    sms_in_thread = Thread(target=sms_receiver, args=(incoming_events,))
#    sms_in_thread.setDaemon(True)
#    sms_in_thread.start()

    # Start SMS sending thread with listening queue
    # queue expects tuples with (number, data)
#    sms_out = Queue()
#    sms_out_thread = Thread(target=sms_sender, args=(sms_out,))
#    sms_out_thread.setDaemon(True)
#    sms_out_thread.start()

    while True:
        processInput()



if __name__ == "__main__":
    main()

# TODO
    # interfacing with web
    # input validation
# if new round starts - start it at event too Event.setRoundId
    # equality ! check types
