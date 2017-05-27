#!/usr/bin/python3

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *

import configparser
from flask import Flask, json, jsonify, make_response, session, render_template, request, send_file
import json
import os
import psycopg2
import queue

class App:
    app = Flask(__name__, static_url_path = "", static_folder = "www")
    SESSION_TYPE = 'Redis'
    app.config.from_object(__name__)
    app.secret_key = "ExtraSecretSessionKey"#os.urandom(24)

    # START BLOCK
    # Player registration

    def registration_template(error):
        return render_template("registration.html", error=error)

    def pending_template():
        if App.logged_in():
            return render_template("pending.html", user=session["user"], phone=session["phone"])
        else:
            return "403 Connection Forbidden"

    def playing_template():
        if App.logged_in():
            return render_template("game_view.html")
        else:
            return "403 Connection Forbidden"

    @app.route("/isJailed")
    def jailed():
        if App.logged_in():
            return str(Event.isPlayerJailed(Player._getIdByName(session["user"])))
        else:
            return "403 Connection Forbidden"

    def logged_in():
        try:
            if session["user"] == None or session["web_hash"] == None:
                return False
            else:
                return True
        except KeyError:
            return False

    @app.route("/")
    def index():
        if App.logged_in():
            if not Event.isPlayerJailed(Player._getIdByName(session["user"])):
                return App.playing_template()
            return App.pending_template()
        else:
            return App.registration_template(" ")

    # Set HTTP headers so those files would not be cached
    @app.route("/events.json")
    def events():
        response = make_response(send_file("www/events.json"))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0'
        return response

    @app.route("/stats.json")
    def stats():
        response = make_response(send_file("www/stats.json"))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0'
        return response

    @app.route("/register", methods=["GET"])
    def new_player():
        user = request.args.get("user")
        phone = request.args.get("phone")

        if user and phone:
            if Action.addPlayer(user, phone, ''):
                session["user"] = user
                session["phone"] = phone
                session["web_hash"] = Player.getHashById(Player._getIdByName(user))
                return App.index()
            else:
                return App.registration_template("Probleem registreerimisel, kontrolli sisestatud andmeid.")
        else:
            return App.registration_template("Mõlemad väljad on kohustuslikud.")


    @app.route("/wrongInfo")
    def wrong_info():
        if App.logged_in():
            phone = request.args.get("phone")
            if phone == session["phone"]:
                Player.delPlayer(session["user"])
                session.clear()
                return "User data removed"
            else:
                return "User data preserved"
        else:
            return "403 Connection Forbidden"

    # Player registration
    # END BLOCK


    # START BLOCK
    # Player actions


    @app.route("/flee")
    def flee_jail():
        fleeing_code = request.args.get("fleeingCode")
        if Action.fleePlayerWithCode(fleeing_code):
            return "You got out"
        else:
            return "Your escape failed"


    @app.route("/tag")
    def tag():
        if App.logged_in():
            tag_code = request.args.get("tagCode")
            if Action.handleWeb(session["web_hash"], tag_code):
                return "Hit"
            else:
                return "Your attempt to catch them failed"
        else:
            return "403 Connection Forbidden"


    @app.route("/messageTeam", methods=["GET"])
    def messageTeam():
        if App.logged_in():
            team_message = request.args.get("message")
            player_id = Player.getIdByHash(session["web_hash"])
            if team_message and player_id:
                if Action.sayToMyTeam(player_id, team_message):
                    return "Message sent"
                else:
                    return "Error sending message"
            else:
                return "Message missing, or invalid player info"
        else:
            return "403 Connection Forbidden"


    # Player actions
    # END BLOCK


    # START BLOCK
    # Getting data

    @app.route("/user")
    def username():
        if App.logged_in():
            return session["user"]
        else:
            return "403 Connection Forbidden"

    @app.route("/userTeam")
    def user_team():
        if App.logged_in():
            if Team.getPlayerTeamId(Player.getIdByHash(session["web_hash"]),Round.getActiveId()):
                return str(Team.getPlayerTeamId(Player.getIdByHash(session["web_hash"]),Round.getActiveId()))
            else:
                return "Player is not currently in a team"
        else:
            return "403 Connection Forbidden"

    @app.route("/baseMessage")
    def base_message():
        try:
            return Action.base_msg_get()["text"]
        except KeyError:
            return ""

    @app.route("/message")
    def personal_message():
        if App.logged_in():
            data = {}
            data['jailed'] = str(Event.isPlayerJailed(Player._getIdByName(session["user"])))
            message = Action.browserRequestsMessages(session["web_hash"])
            data['message'] = message
            return jsonify(data)
        else:
            return "403 Connection Forbidden"

    # Getting data
    # END BLOCK


    # START BLOCK
    # Spawnmaster screen

    def spawn_view():
        if App.is_master():
            Round.updateActiveId()
            players, teamless = Stats.playersDetailed()
            rounds = Round.getRounds()
            return render_template("spawn.html", rounds=rounds, teamless=teamless, players = players)
        else:
            return "403 Connection Forbidden"

    def is_master():
        try:
            if session["master"] == 1:
                return True
            else:
                return False
        except KeyError:
            return False

    @app.route("/spawn")
    def spawnmaster():
        if App.is_master():
            return App.spawn_view()
        else:
            return render_template("spawn_login.html")

    @app.route("/masterLogin", methods=["GET"])
    def master_login():
        user = request.args.get("user")
        password = request.args.get("pw")

        if user == config['users']['spawnuser'] and \
            password == config['users']['spawnpassword']:
            session["master"] = 1
            return App.spawnmaster()
        else:
            return "403 Connection Forbidden"

    @app.route("/masterout")
    def master_logout():
        if App.is_master():
            session.clear()
            return "Spanwmaster has logged out"
        else:
            return "403 Connection Forbidden"

    # Spawnmaster screen
    # END BLOCK

    # START BLOCK
    # Stats screens

    @app.route("/baseLogin", methods=["GET"])
    def base_login():
        user = request.args.get("user")
        password = request.args.get("pw")

        if user == config['users']['baseuser'] and \
            password == config['users']['basepassword']:
            session["base"] = 1
            return App.base_template()
        else:
            return "403 Connection Forbidden"

    def is_base():
        try:
            if session["base"] == 1:
                return True
            else:
                return False
        except KeyError:
            return False

    @app.route("/base")
    def base_template():
        if App.is_base():
            return render_template("base.html")
        else:
            return render_template("base_login.html")

    @app.route("/spectate")
    def spectator_template():
        return render_template("spectate.html")

    @app.route("/baseout")
    def base_logout():
        if App.is_base():
            session.clear()
            return "Basemaster has logged out"
        else:
            return "403 Connection Forbidden"

    # Stats screens
    # END BLOCK


    # START BLOCK
    # Spawnmaster's actions

    # Adding a new round
    @app.route("/addRound", methods=["GET"])
    def startRound():
        roundName = request.args.get("roundName")
        # How many minutes does the round last
        roundLength = request.args.get("roundLength")
        # In how many minutes does the round begin
        startsAt = request.args.get("startsAt")
        try:
            int(roundLength)
            #int(startsIn)
        except ValueError:
            return "Round length and starttime has to be entered as integers."
        startTime = datetime.datetime.now()
        startTime = startTime.replace(hour=int(startsAt[0:2]), minute=int(startsAt[3:5]), second=0, microsecond=0)
        endTime = startTime + datetime.timedelta(seconds = int(roundLength) * 60)
        startTimeString = format(startTime, dateformat)
        endTimeString = format(endTime, dateformat)
        if not roundName or not roundLength or not startsAt:
            return "Insufficient info for a new round"
        else:
            if Round.add(roundName, startTimeString, endTimeString):
                Action.addTeamsToAllRounds()
                return "New round \"" + roundName + "\" start time " + startTimeString + ", end time " + endTimeString + "."
            else:
                return "Error: New round has overlapping time. not added: \"" + roundName + "\" start time " + startTimeString + ", end time " + endTimeString + "."



    # Adding player to a team in active round
    @app.route("/addToTeam", methods = ["GET"])
    def addToTeam():
        team_name = request.args.get("teamName")
        player_id = request.args.get("playerId")
        if team_name and player_id:
            try:
                Action.addPlayerToTeam(Player.getNameById(player_id), team_name)
                return "Player " + Player.getNameById(player_id) + " added to team" + team_name
            except:
                return "Team or player id were given as invalid values."
        else:
            return "Missing team or player id."


    # Spawnmaster's actions
    # END BLOCK


    # Routes for SMS
    @app.route("/sms", methods=['GET'])
    def smsserver():
        # Check the stupid "password"
        if request.args.get('pass') != 'avf2DA3XeJZmqy9KKVjFdGfU':
            return jsonify({'error': 'error'})
        # Receive incoming SMSes
        incoming = json.loads(request.data.decode('utf8'))
        for message in incoming['incoming']:
            # Act on the message, it's something similar to
            # {'number': 512314, 'contents': 'Welcome here',
            #  'sent': sent, 'received': received}
            #print(message)
            Action.handleSms(message['number'], message['contents'])
        # Mark all the old enough messages ready for SMSing
        Action.messages_timeout_check()
        out = []
        try:
            while True:
                element = sms_queue.get_nowait()
                out.append(element)
        except queue.Empty:
            pass
        return jsonify({'outgoing': out})


    # Routes for printing
    @app.route("/print", methods=['GET'])
    def printserver():
        if request.args.get('pass') != 'htpT2U8UMpApV852DGSncBP7':
            return jsonify({'error': 'error'})
        data = []
        try:
            while True:
                element = printer_queue.get_nowait()
                data.append(element)
        except queue.Empty:
            pass
        return jsonify({'print': data})


if __name__ == "__main__":
    # Start program
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Connect to database
    try:
        db = config['database']
        parameters = "host='%s' dbname='%s' user='%s' password='%s'" % (
            db['host'], db['dbname'], db['user'], db['password'])
        connection = psycopg2.connect(parameters)
        connection.set_session(autocommit=True)
        cursor = connection.cursor()
    except:
        print ("Error. Unable to connect to the database. If losing data is acceptable, try running 'python reset_db.py'")
        exit()

    # Queues
    sms_queue = queue.Queue()
    printer_queue = queue.Queue()

    Action.initAllConnect(cursor, sms_queue, printer_queue)
    Round.updateActiveId()
    Stats.updateStats()
    Stats.printPlayersDetailed()

    debug = False
    if debug:
        App.app.run(debug=True)
    else:
        import logging
        from threading import Thread
        from engine.cli import processInput

        logging.basicConfig(filename='flask.log', level=logging.DEBUG)

        appthread = Thread(target=App.app.run, args=())
        appthread.setDaemon(True)
        appthread.start()

        while True:
            processInput()
