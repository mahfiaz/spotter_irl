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


app = Flask(__name__)
SESSION_TYPE = 'Redis'
app.config.from_object(__name__)
app.secret_key = os.urandom(24)

teamName1 = "Sinised"
teamName2 = "Punased"


# START BLOCK
# Player registration


def registrationTemplate():
	return render_template("playerRegistration.html")

@app.route("/")
def isLoggedin():
	try:
		if session["user"] == None:
			return registrationTemplate()
		else:
			return render_template("playerPending.html", user=session["user"], phone=session["phone"], email=session["email"])
	except KeyError:
		return registrationTemplate()


@app.route("/register", methods = ["GET"])
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

# Player registration
# END BLOCK



# START BLOCK
# Spawnmaster screen


@app.route("/masterlogin")
def masterLoginTemplate():
	return render_template("masterLogin.html")


def masterView():
	return render_template("base.html")


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
		return registrationTemplate()


@app.route("/login", methods=["GET"])
def masterLogin():
	#TODO Use POST method for logging in here
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

# Spawnmaster screen
# END BLOCK



# START BLOCK
# Routes to player screen templates


@app.route("/tag")
def tag():
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

Action.initAllOnce(cursor)
Spawn.initOnce(cursor)


if __name__ == "__main__":
	app.run()