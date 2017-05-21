#!/usr/bin/python3

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *
from engine.spawn import *

import connect
from flask import Flask, render_template, request, json, session, jsonify
import json
import os
import queue


app = Flask(__name__, static_url_path = "", static_folder = "www")
SESSION_TYPE = 'Redis'
app.config.from_object(__name__)
app.secret_key = os.urandom(24)


# START BLOCK
# Player registration


def registration_template(error):
    return render_template("regi", error=error)

def pending_template():
	if logged_in():
		return render_template("pending", user=session["user"], phone=session["phone"])
	else:
		return "403 Connection Forbidden"

@app.route("/p")
def playing_template():
	if logged_in():
		return render_template("p_stats")
	else:
		return "403 Connection Forbidden"

@app.route("/isJailed")
def playing_templateasd():
	if logged_in():
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
	if logged_in():
		if not Event.isPlayerJailed(Player._getIdByName(session["user"])):
			return playing_template()
		return pending_template()
	else:
		return registration_template("")


@app.route("/register", methods=["GET"])
def new_player():
	user = request.args.get("user")
	phone = request.args.get("phone")

	if user and phone:
		if Action.addPlayerWOEmail(user, phone):
			session["user"] = user
			session["phone"] = phone
			session["web_hash"] = Player.getHashById(Player._getIdByName(user))
			return index()
		else:
			return registration_template("Nimi või mobiil juba kasutusel.")
	else:
		return registration_template("Mõlemad väljad on kohustuslikud.")


@app.route("/wrongInfo")
def wrong_info():
	if logged_in():
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
		return "Said põgenema"
	else:
		return "Põgenemiskatse nurjus"


@app.route("/tag")
def tag():
	if logged_in():
		tag_code = request.args.get("tagCode")
		if Action.handleWeb(session["web_hash"], tag_code):
			return "Tabasid"
		else:
			return "Ebaõnnestunud katse"
	else:
		return "403 Connection Forbidden"

# Player actions
# END BLOCK


# START BLOCK
# Getting data

@app.route("/user")
def userName():
	if logged_in():
		return session["user"]
	else:
		return "403 Connection Forbidden"

@app.route("/events")
def events():
	try:
		with open('events.json') as data_file:
			events = json.load(data_file)
		response = jsonify(events)
		return response
	except:
		return "File not found"
	
@app.route("/stats")
def stats():
	try:
		with open('stats.json') as data_file:
			stats = json.load(data_file)
		response = jsonify(stats)
		return response
	except:
		return "File not found"
	

# Getting data
# END BLOCK


# START BLOCK
# Spawnmaster screen

def master_login_template():
    return render_template("m_auth")

def master_view():
	if is_master():
		Round.updateActiveId()
		players, teamless = Stats.playersDetailed()
		rounds = Round.getRounds()
		return render_template("master", rounds=rounds, teamless=teamless, players = players)
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
    if is_master():
        return master_view()
    else:
        return master_login_template()

@app.route("/masterLogin", methods=["GET"])
def master_login():
    try:
        user = request.args.get("user")
        pw = request.args.get("pw")
        acc = Spawn.login()

        if user == acc["name"][0] and pw == acc["pw"][0]:
            session["master"] = 1
            return spawnmaster()
        else:
            return "403 Connection Forbidden"
    except:
        return "403 Connection Forbidden"

@app.route("/masterout")
def master_logout():
	if is_master():
		session.clear()
		return "Spanwmaster has logged out"
	else:
		return "403 Connection Forbidden"

# Spawnmaster screen
# END BLOCK


# START BLOCK
# Stats screens

def base_login_template():
	return render_template("b_auth")

@app.route("/baseLogin", methods=["GET"])
def base_login():
    try:
        user = request.args.get("user")
        pw = request.args.get("pw")

        if user == "base" and pw == "master":
            session["base"] = 1
            return base_template()
        else:
            return "403 Connection Forbidden"
    except:
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
	if is_base():
		return render_template("stats")
	else:
		return base_login_template()

@app.route("/spectate")
def spectator_template():
	return render_template("spectate")

@app.route("/baseout")
def base_logout():
	if is_base():
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
        return "Puudulik info uue roundi jaoks."
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
    if request.args.get('pass') != 'avf2DA3XeJZmqy9KKVjFdGfU':
        return jsonify({'tervitus': 'mineara'})
    data = {'outgoing': []}
    while True:
        try:
            element = sms_outgoing.get_nowait()
            data['outgoing'].append(element)
        except queue.Empty:
            break
    return jsonify(data)


# Routes for printing
@app.route("/print", methods=['GET'])
def printserver():
    if request.args.get('pass') != 'htpT2U8UMpApV852DGSncBP7':
        return jsonify({'tervitus': 'mineara'})
    data = {'spool': []}
    while True:
        try:
            element = printer_queue.get_nowait()
            data['spool'].append(element)
        except queue.Empty:
            break
    return jsonify(data)


if __name__ == "__main__":
    # Start program
    try:
        connection = connect.connectDB()
    except:
        print("Problem with the database connection")
    cursor = connection.cursor()

    # Queues 
    sms_queue = queue.Queue()
    printer_queue = queue.Queue()

    Action.initAllConnect(cursor, sms_queue, printer_queue)
    Round.updateActiveId()
    Stats.updateStats()
    Stats.printPlayersDetailed()

    debug = False
    if debug:
        app.run(debug=True)
    else:
        from threading import Thread
        from engine.cli import processInput

        appthread = Thread(target=app.run, args=())
        appthread.setDaemon(True)
        appthread.start()

        while True:
            processInput()

