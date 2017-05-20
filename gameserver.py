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


app = Flask(__name__, static_url_path = "", static_folder = "www/static")
SESSION_TYPE = 'Redis'
app.config.from_object(__name__)
app.secret_key = os.urandom(24)







# START BLOCK
# Player registration


def registration_template():
	return render_template("regi")

def pending_template():
	return render_template("pending", user=session["user"], phone=session["phone"])

@app.route("/ps")
def playing_template():
	return render_template("p_stats")

def login_status():
	try:
		if session["user"] == None:
			return False
		else:
			return True
	except KeyError:
		return False


@app.route("/logstat")
def login_status1():
	try:
		if session["user"] == None:
			return str(False)
		else:
			return str(True)
	except KeyError:
		return str(False)

@app.route("/")
def index():
	if login_status() and is_free():
		return playing_template()
	elif login_status():
		return pending_template()
	else:
		return registration_template()


@app.route("/register", methods=["GET"])
def save_new():
	_user = request.args.get("user")
	_phone = request.args.get("phone")
	session["user"] = _user
	session["phone"] = _phone

	if _user and _phone:
		if Action.addPlayerWOEmail(_user, _phone):
			return index()
		else:
			return registration_template()
	else:
		return registration_template()


@app.route("/wrongInfo")
def wrong_info():
	Player.delPlayer(session["user"])
	session.clear()
	return "User data removed"

def is_free():
	if login_status:
		user = session["user"]
		try:
			with open('stats.json') as data_file:
				stats = json.load(data_file)
			if stats["roundName"] != None:
				for player in stats["teamlessPlayers"]:
					if player["name"] == user:
						return player["nowInLiberty"]
				for team in stats["teams"]:
					for player in team["players"]:
						if player["name"] == user:
							return player["nowInLiberty"]
			else:
				return False
		except:
			return False


@app.route("/jf")
def is_free1():
	if login_status:
		user = session["user"]
		try:
			with open('stats.json') as data_file:
				stats = json.load(data_file)
			if stats["roundName"] != None:
				for player in stats["teamlessPlayers"]:
					if player["name"] == user:
						return str(player["nowInLiberty"])+" - teamless"
				for team in stats["teams"]:
					for player in team["players"]:
						if player["name"] == user:
							return str(player["nowInLiberty"])+" - in team"
			else:
				return "False - roundname == none"
		except:
			return "False - no file"


# Player registration
# END BLOCK


# START BLOCK
# Getting data

@app.route("/user")
def userName():
	if login_status():
		return session["user"]

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
def hue():
	with open('events.json') as data_file:
		events = json.load(data_file)
	with open('stats.json') as data_file:
		stats = json.load(data_file)
	return render_template("stats", events = events, stats = stats)
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


@app.route("/tagging")
def tagging():
	user = "rjurik"
	team = 2
	if team == 1:
		team = "blue"
	else:
		team = "red"
	score = 520
	rank = 3
	return render_template("playerPlaying.html", user=user, team=team, score=score, rank=rank)

@app.route("/tagged")
def tagged():
	user = "rjurik"
	team = 1
	if team == 1:
		team = "blue"
	else:
		team = "red"
	score = 520
	rank = 3
	tagger = "LOLer"
	return render_template("playerTagged.html", team=team, tagger=tagger, user=user, score=score, rank=rank)


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
