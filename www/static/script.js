userJailed = "";
gameServerAdress = "http://localhost:5000/";

function getAllStats() {
	var xhrStats = new XMLHttpRequest();
	var stats = "";
	var divContents = "";
	var isDiv = false;

	xhrStats.open("GET", "/stats", true);
	xhrStats.send();
	xhrStats.onreadystatechange = function() {
		if (xhrStats.readyState == 4 && xhrStats.status == 200) {
			stats = xhrStats.responseText;
			stats = JSON.parse(stats);
			if (document.getElementById("stats")) {
				isDiv = true;
				var statsDiv = document.getElementById("stats");
			}
			
			if(stats["roundName"] != null) {
				divContents += "<table style='width:100%;'><tr><th></th><th>Tabatud</th><th>Puude</th><th>Miinus</th><th>Skoor</th></tr>";
				for(i in stats["teams"]) {
					team = stats["teams"][i];
					divContents += "<tr style='color:#"+team["color"]+";'><th>"+team["name"]+"</th><th>"+team["spotCount"]+"</th><th>"+team["touchCount"]+"</th><th>"+team["disloyality"]+"</th><th>"+team["score"]+"</th></tr>";
					for (i in team["players"]) {
						player = team["players"][i];
						divContents += "<tr style='color:#"+team["color"]+";'><td>"+player["name"]+"</td><td>"+player["spotCount"]+"</td><td>"+player["touchCount"]+"</td><td>"+player["disloyality"]+"</td><td>"+player["score"]+"</td></tr>";
					}
				}
				divContents += "</table>";
				divContents += "<div class='bottom' id='toEnd'></div>";
				if (isDiv) {
					statsDiv.innerHTML = divContents;
				}
			} else {
				if (isDiv) {
					statsDiv.innerHTML = "";
				}
			}
		}
	}
}




function getAllEvents() {
	var xhrEvents = new XMLHttpRequest();
	var events = "";
	var divContents = "";
	var isDiv = false;

	if (document.getElementById("events")) {
		var eventsDiv = document.getElementById("events");
		isDiv = true;
	}

	xhrEvents.open("GET", "/events", true);
	xhrEvents.send();
	xhrEvents.onreadystatechange = function() {
		if (xhrEvents.readyState == 4 && xhrEvents.status == 200) {
			events = xhrEvents.responseText;
			events = JSON.parse(events);
			if("event" in events[0]) {
				console.log("No events to show");
				if (isDiv) {
					eventsDiv.innerHTML = "";
				}
			} else {
				eventsDiv.innerHTML = divContents;
				for(i in events) {
					event = events[i];
					if (event["visible"] == "All") {
						divContents += "<p>"+event["time"];
						divContents += " <span style='color:#"+event["text1"]["color"]+";'>"+event["text1"]["text"]+"</span>";
						divContents += " <span style='color:#"+event["text2"]["color"]+";'>"+event["text2"]["text"]+"</span>";
						if (event["text3"]["text"] != null) {
							divContents += " <span style='color:#"+event["text3"]["color"]+";'>"+event["text3"]["text"]+"</span>";
						}
						divContents += "</p>";
					}
				}
				if (isDiv) {
					eventsDiv.innerHTML = divContents;
				}
			}
		}
	}
}



function getRoundInfoBase(role) {
	var xhrRound = new XMLHttpRequest();
	var stats = "";
	var user = "";
	var divContents = "";
	var isDiv = false;

	if (document.getElementById("roundInfo")) {
		var roundDiv = document.getElementById("roundInfo");
		isDiv = true;
	}

	xhrRound.open("GET", "/stats", true);
	xhrRound.send();
	xhrRound.onreadystatechange = function() {
		if (xhrRound.readyState == 4 && xhrRound.status == 200) {
			stats = xhrRound.responseText;
			stats = JSON.parse(stats);
			if(stats["roundName"] != null) {
				divContents += "<p>Lahing \"" + stats["roundName"] + "\", Kasutaja: " + role + "</p>";
				if (isDiv) {
					roundDiv.innerHTML = divContents;
				}
			}
		}
	}
}



function getStats() {
	var xhrStats = new XMLHttpRequest();
	var xhrPlayer = new XMLHttpRequest();
	var stats = "";
	var user = "";
	var divContents = "";
	var isDiv = false;

	xhrPlayer.open("GET", "/user", true);
	xhrPlayer.send();
	xhrPlayer.onreadystatechange = function() {
		if (xhrPlayer.readyState == 4 && xhrPlayer.status == 200) {
			user = xhrPlayer.responseText;
		}
	}

	xhrStats.open("GET", "/stats", true);
	xhrStats.send();
	xhrStats.onreadystatechange = function() {
		if (xhrStats.readyState == 4 && xhrStats.status == 200) {
			stats = xhrStats.responseText;
			stats = JSON.parse(stats);
			if (document.getElementById("stats")) {
				isDiv = true;
				var statsDiv = document.getElementById("stats");
			}
			
			if(stats["roundName"] != null) {
				divContents += "<table style='width:100%;'><tr><th></th><th>Tabatud</th><th>Puude</th><th>Miinus</th><th>Skoor</th></tr>";
				for(i in stats["teams"]) {
					team = stats["teams"][i];
					divContents += "<tr style='color:#"+team["color"]+";'><th>"+team["name"]+"</th><th>"+team["spotCount"]+"</th><th>"+team["touchCount"]+"</th><th>"+team["disloyality"]+"</th><th>"+team["score"]+"</th></tr>";
				}
				for(i in stats["teams"]) {
					team = stats["teams"][i];
					for (i in team["players"]) {
						player = team["players"][i];
						if (player["name"] == user) {
							divContents += "<tr style='color:#"+team["color"]+";'><td>"+player["name"]+"</td><td>"+player["spotCount"]+"</td><td>"+player["touchCount"]+"</td><td>"+player["disloyality"]+"</td><td>"+player["score"]+"</td></tr></table>";
						}
					}
				}
				for(i in stats["teamlessPlayers"]) {
					player = stats["teamlessPlayers"][i];
					if(player["name"] == user) {
						divContents += "<tr><td>"+player["name"]+"</td><td>"+player["spotCount"]+"</td><td>"+player["touchCount"]+"</td><td>"+player["disloyality"]+"</td><td>"+player["score"]+"</td></tr></table>";
					}
				}
				divContents += "<div class='bottom' id='toEnd'></div>";
				if (isDiv) {
					statsDiv.innerHTML = divContents;
				}
			} else {
				if (isDiv) {
					statsDiv.innerHTML = "";
				}
			}
		}
	}
}



function getEvents() {
	var xhrEvents = new XMLHttpRequest();
	var xhrPlayer = new XMLHttpRequest();
	var xhrTeam = new XMLHttpRequest();
	var events = "";
	var user = "";
	var userTeam = "";
	var divContents = "";
	var isDiv = false;

	if (document.getElementById("events")) {
		var eventsDiv = document.getElementById("events");
		isDiv = true;
	}

	xhrPlayer.open("GET", "/user", true);
	xhrPlayer.send();
	xhrPlayer.onreadystatechange = function() {
		if (xhrPlayer.readyState == 4 && xhrPlayer.status == 200) {
			user = xhrPlayer.responseText;
		}
	}


	xhrTeam.open("GET", "/userTeam", true);
	xhrTeam.send();
	xhrTeam.onreadystatechange = function() {
		if (xhrTeam.readyState == 4 && xhrTeam.status == 200) {
			userTeam = xhrTeam.responseText;
		}
	}


	xhrEvents.open("GET", "/events", true);
	xhrEvents.send();
	xhrEvents.onreadystatechange = function() {
		if (xhrEvents.readyState == 4 && xhrEvents.status == 200) {
			events = xhrEvents.responseText;
			events = JSON.parse(events);
			if("event" in events[0]) {
				console.log("No events to show");
				if (isDiv) {
					eventsDiv.innerHTML = "";
				}
			} else {
				for(i in events) {
					event = events[i];
					if (event["visible"] == "All" || (event["visible"] == "Sinised" && userTeam == "1") || (event["visible"] == "Punased" && userTeam == "2")) {
						divContents += "<p>"+event["time"];
						divContents += " <span style='color:#"+event["text1"]["color"]+";'>"+event["text1"]["text"]+"</span>";
						divContents += " <span style='color:#"+event["text2"]["color"]+";'>"+event["text2"]["text"]+"</span>";
						if (event["text3"]["text"] != null) {
							divContents += " <span style='color:#"+event["text3"]["color"]+";'>"+event["text3"]["text"]+"</span>";
						}
						divContents += "</p>";
					}
				}
				if (isDiv) {
					eventsDiv.innerHTML = divContents;
				}
			}
		}
	}
}


function getRoundInfo() {
	var xhrRound = new XMLHttpRequest();
	var xhrPlayer = new XMLHttpRequest();
	var stats = "";
	var user = "";
	var divContents = "";
	var isDiv = false;

	if (document.getElementById("roundInfo")) {
		var roundDiv = document.getElementById("roundInfo");
		isDiv = true;
	}

	xhrPlayer.open("GET", "/user", true);
	xhrPlayer.send();
	xhrPlayer.onreadystatechange = function() {
		if (xhrPlayer.readyState == 4 && xhrPlayer.status == 200) {
			user = xhrPlayer.responseText;
		}
	}

	xhrRound.open("GET", "/stats", true);
	xhrRound.send();
	xhrRound.onreadystatechange = function() {
		if (xhrRound.readyState == 4 && xhrRound.status == 200) {
			stats = xhrRound.responseText;
			stats = JSON.parse(stats);
			if(stats["roundName"] != null) {
				divContents += "<p>Lahing \"" + stats["roundName"] + "\", mängija: " + user +"</p>";
				if (isDiv) {
					roundDiv.innerHTML = divContents;
				}
			}
		}
	}
}


function timeToEnd() {
	var xhrTime = new XMLHttpRequest();
	currentDate = new Date();
	var isDiv = false;

	if (document.getElementById("roundInfo")) {
		var roundDiv = document.getElementById("roundInfo");
		isDiv = true;
	}

	xhrTime.open("GET", "/stats", true);
	xhrTime.send();
	xhrTime.onreadystatechange = function() {
		if (xhrTime.readyState == 4 && xhrTime.status == 200) {
			stats = xhrTime.responseText;
			stats = JSON.parse(stats);
			if(stats["roundName"] != null) {
				var ending = stats["roundEnd"];
				endTime = new Date(ending.substring(0,4),ending.substring(5,7),ending.substring(8,10),ending.substring(11,13),ending.substring(14,16),ending.substring(17,19));
				var timeDiv = document.getElementById("toEnd");
				var toEnd = new Date(endTime.getTime() - currentDate.getTime());
				var divContents = "Aega vooru lõpuni " + addZerobefore(toEnd.getUTCHours()) + ":" + addZerobefore(toEnd.getUTCMinutes()) + ":" + addZerobefore(toEnd.getUTCSeconds());
				if (isDiv) {
					timeDiv.innerHTML = divContents;
				}
			}
		}
	}
}


function isJailed() {
	if (document.getElementById("isJailed")) {
        $.ajax({
            url: "isJailed"
        }).done(function(data) {
        	userJailed = data;
        });
	}
}


function addZerobefore(number) {
	if(parseInt(number) < 10 && parseInt(number) > -10) {
		number = "0" + parseInt(number);
	}
	return number;
}