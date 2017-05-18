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


app = Flask(__name__)
SESSION_TYPE = 'Redis'
app.config.from_object(__name__)
app.secret_key = os.urandom(24)


# START BLOCK
# Player registration


def registrationTemplate():
	return render_template("regi")

@app.route("/")
def isLoggedin():
	try:
		if session["user"] == None:
			return registrationTemplate()
		else:
			return render_template("pending", user=session["user"], phone=session["phone"], email=session["email"])
	except KeyError:
		return registrationTemplate()


@app.route("/register", methods=["GET"])
def saveNew():
	_user = request.args.get("user")
	_phone = request.args.get("phone")
	_email = request.args.get("email")
	session["user"] = _user
	session["phone"] = _phone
	session["email"] = _email

	if _user and _phone:
		if Action.addPlayer(_user, _phone, _email):
			return isLoggedin()
		else:
			return registrationTemplate()
	else:
		return registrationTemplate()


@app.route("/wrongInfo")
def wrongInfo():
	Player.delPlayer(session["user"])
	session.clear()
	return "User data removed"


@app.route("/status")
def jailStatus():
	_user = session["user"]


# Player registration
# END BLOCK


# START BLOCK
# Player actions

@app.route("/flee", methods = ["GET"])
def flee():
	code = request.args.get("tagCode")
	try:
		Action.fleePlayerWithCode(code)
		return "Pääsesid"
	except:
		return "Oled kindle, et sisestasid koodi?"


@app.route("/tag", methods = ["GET"])
def tag():
	#TODO login control (for webhash)
	tag_code = request.args.get("tagCode")
	web_hash = session["web_hash"]
	Action.handleWeb(web_hash, tag_code)


# Player actions
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