#!/usr/bin/python3

import connect

from engine.event import *
from engine.action import *
from engine.code import *
from engine.player import *
from engine.round import *
from engine.team import *
from engine.spawn import *

from flask import Flask, render_template, request, json, session, jsonify
import os
import json


app = Flask(__name__, static_url_path = "", static_folder = "www")
SESSION_TYPE = 'Redis'
app.config.from_object(__name__)
app.secret_key = os.urandom(24)


# START BLOCK
# Player registration


def registration_template():
	return render_template("regi")

def pending_template():
	if logged_in():
		return render_template("pending", user=session["user"], phone=session["phone"])
	else:
		return "403 Connection Forbidden"

#@app.route("/p")
def playing_template():
	if logged_in():
		return render_template("p_stats")
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
		return registration_template()


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
			return registration_template()
	else:
		return registration_template()


@app.route("/wrongInfo")
def wrong_info():
	if logged_in():
		Player.delPlayer(session["user"])
		session.clear()
		return "User data removed"
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


@app.route("/masterlogin")
def masterLoginTemplate():
	return render_template("m_auth")


def masterView():
	players, teamless = Stats.playersDetailed()
	for person in teamless:
		print(person)
	rounds = Round.getRounds()
	return render_template("master", rounds=rounds, teamless=teamless)


def isMaster():
	try:
		if session["master"] == 1:
			return True
		else:
			return False
	except KeyError:
		return False


@app.route("/spawn")
def spawnmaster():
	if isMaster():
		return masterView()
	else:
		return masterLoginTemplate()


@app.route("/login", methods=["GET"])
def masterLogin():
	try:
		_user = request.args.get("user")
		_pw = request.args.get("pw")
		acc = Spawn.login()

		if _user == acc["name"][0] and _pw == acc["pw"][0]:
			session["master"] = 1
			return spawnmaster()
		else:
			return "Connection foridden"
	except:
		return "Connection forbidden"


@app.route("/masterout")
def masterLogout():
	session.clear()
	return "Spanwmaster has logged out"


@app.route("/s")
def base_Template():
	return render_template("stats")
# Spawnmaster screen
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
	startsIn = request.args.get("startsIn")
	try:
		int(roundLength)
		int(startsIn)
	except ValueError:
		return "Round length and starttime has to be entered as integers."
	startTime = datetime.datetime.now() + datetime.timedelta(seconds = int(startsIn) * 60)
	endTime = startTime + datetime.timedelta(seconds = int(roundLength) * 60)
	startTimeString = format(startTime, dateformat)
	endTimeString = format(endTime, dateformat)
	if not roundName or not roundLength or not startsIn:
		return "Puudulik info uue roundi jaoks."
	else:
		if Round.add(roundName, startTimeString, endTimeString):
			return "New round \"" + roundName + "\" start time " + startTimeString + ", end time " + endTimeString + "."
		else:
			return "Error: New round has overlapping time. not added: \"" + roundName + "\" start time " + startTimeString + ", end time " + endTimeString + "."



# Adding player to a team in a round
@app.route("/addToTeam", methods = ["GET"])
def addToTeam():
	roundId = request.args.get("roundId")
	playerId = request.args.get("playerId")
	if roundId and playerId:
		try:
			team.add(playerId, roundId)
			return "Player " + Player.getNameById(playerId) + " added to round" + roundId
		except:
			return "Round or player id were given as invalid values."
	else:
		return "Missing round or player id."


# Spawnmaster's actions
# END BLOCK



# START BLOCK
# Routes to player screen templates


# Routes to player screen templates
# END BLOCK



# Start program

try:
	connection = connect.connectDB()
except:
    print("Problem with the database connection")
cursor = connection.cursor()

Action.initAllConnect(cursor)
Round.updateActiveId()


if __name__ == "__main__":
	app.run(debug=True)
