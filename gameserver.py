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
            return render_template("pending.html", user=request.cookies.get("user"), phone=request.cookies.get("phone"))
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
            return str(Event.isPlayerJailed(Player._getIdByName(request.cookies.get("user"))))
        else:
            return "403 Connection Forbidden"

    def logged_in():
        try:
            if request.cookies.get("user") == None or request.cookies.get("web_hash") == None:
                return False
            else:
                return True
        except KeyError:
            return False

    @app.route("/login", methods=["GET"])
    def login():
        web_hash = request.args.get("hash")
        phone = Player.getMobileById(Player.getIdByHash(web_hash))
        user = Player.getNameById(Player.getIdByHash(web_hash))
        return App.add_cookies(user, phone, web_hash)
        

    @app.route("/")
    def index():
        if App.logged_in():
            if not Event.isPlayerJailed(Player._getIdByName(request.cookies.get("user"))):
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
                return App.add_cookies(user, phone, Player.getHashById(Player._getIdByName(user)))
            else:
                return App.registration_template("Probleem registreerimisel, kontrolli sisestatud andmeid.")
        else:
            return App.registration_template("Mõlemad väljad on kohustuslikud.")

    @app.route("/cookie")
    def add_cookies(user, phone, web_hash):
        try:
            expire_date = datetime.datetime.now()
            expire_date = expire_date + datetime.timedelta(days=1)
            cookies = make_response(render_template("to_game.html"))
            cookies.set_cookie("user", user, expires=expire_date)
            cookies.set_cookie("phone", phone, expires=expire_date)
            cookies.set_cookie("web_hash", web_hash, expires=expire_date)
            return cookies
        except:
            return "Problem adding cookies"

    @app.route("/delCookies")
    def delete_cookies():
        try:
            cookies = make_response(render_template("to_game.html"))
            cookies.set_cookie("user", "", expires=0)
            cookies.set_cookie("phone", "", expires=0)
            cookies.set_cookie("web_hash", "", expires=0)
            return cookies
        except:
            return "Problem adding cookies"

    @app.route("/wrongInfo")
    def wrong_info():
        if App.logged_in():
            phone = request.args.get("phone")
            if phone == request.cookies.get("phone"):
                Player.delPlayer(request.cookies.get("user"))
                return App.delete_cookies()
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
            if Action.handleWeb(request.cookies.get("web_hash"), tag_code):
                return "Hit"
            else:
                return "Your attempt to catch them failed"
        else:
            return "403 Connection Forbidden"


    @app.route("/messageTeam", methods=["GET"])
    def messageTeam():
        if App.logged_in():
            team_message = request.args.get("message")
            player_id = Player.getIdByHash(request.cookies.get("web_hash"))
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
            return request.cookies.get("user")
        else:
            return "403 Connection Forbidden"

    @app.route("/userTeam")
    def user_team():
        if App.logged_in():
            if Team.getPlayerTeamId(Player.getIdByHash(request.cookies.get("web_hash")),Round.getActiveId()):
                return str(Team.getPlayerTeamId(Player.getIdByHash(request.cookies.get("web_hash")),Round.getActiveId()))
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
            data['jailed'] = str(Event.isPlayerJailed(Player._getIdByName(request.cookies.get("user"))))
            message = Action.browserRequestsMessages(request.cookies.get("web_hash"))
            data['message'] = message
            return jsonify(data)
        else:
            return "403 Connection Forbidden"

    @app.route("/teams")
    def teams():
        all_teams = []
        for team in game_config.teams:
            all_teams.append(team['name'])
        return jsonify(all_teams)

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

    @app.route("/getcode", methods=["GET"])
    def getcode():
        # expects request /getcode?site=A
        site = request.args.get("site")
        if site not in ['A', 'B']:
            return "403 Connection Forbidden"
        code, shortcode = game.sites[site].lock()
        data = {'code': code, 'shortcode': shortcode}
        return jsonify(data)

    @app.route("/unlock", methods=["GET"])
    def unlock():
        # expects request /getcode?site=A
        site = request.args.get("s")
        code = request.args.get("c")
        if site not in ['A', 'B']:
            return "403 Connection Forbidden"
        print(site, code)
        data = {}
        data['response'] = game.sites[site].unlock(code)
        return jsonify(data)

    @app.route("/pollsite", methods=["GET"])
    def pollsite():
        site = request.args.get("site")
        if site not in ['A', 'B']:
            return "403 Connection Forbidden"
        data = {}
        s = game.sites[site]
        # Check if keypad was unlocked
        data['lock'] = s.locked
        if s.starting:
            data['startround'] = True
            s.starting = False
        return jsonify(data)

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

    game = Game(config, cursor)

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
