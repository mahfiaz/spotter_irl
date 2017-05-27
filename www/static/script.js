user = "";
userTeam = "";
userJailed = "";
gameServerAddress = window.location.origin + "/";

function getAllStats() {
    if (document.getElementById("stats")) {
        var divContents = "";
        $.ajax({
            url: "stats.json?time="+Date.now()
        }).done(function(stats) {
            if (stats["roundName"] == null) {
                console.log("No active round");
                $("#stats").html("");
            } else {
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
                $("#stats").html(divContents);
            }
        });
    }
}


function getAllEvents() {
    if (document.getElementById("events")) {
        var divContents = "";
        $.ajax({
            url: "events.json?time="+Date.now()
        }).done(function(events) {
            if ("event" in events[0]) {
                console.log("No events to show");
                $("#events").html("");
            } else {
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
                $("#events").html(divContents);
            }
        });
    }
}


function getRoundInfoBase(role) {
    if (document.getElementById("roundInfo")) {
        $.ajax({
            url: "stats.json?time="+Date.now()
        }).done(function(stats) {
            if(stats["roundName"] != null) {
                $("#roundInfo").html("<p>Lahing \"" + stats["roundName"] + "\", Kasutaja: " + role + "</p>");
            } else {
                $("#roundInfo").html("");
            }
        });
    }
}



function getStats() {
    if (document.getElementById("stats")) {
        var divContents = "";
        $.ajax({
            url: "stats.json?time="+Date.now()
        }).done(function(stats) {
            if(stats["roundName"] != null) {
                divContents += "<table style='width:100%;'><tr><th></th><th>Tabatud</th><th>Puude</th><th>Miinus</th><th>Skoor</th></tr>";
                for(i in stats["teams"]) {
                    team = stats["teams"][i];
                    divContents += "<tr style='color:#"+team["color"]+";'><th>"+team["name"]+"</th><th>"+team["spotCount"]+"</th><th>"+team["touchCount"]+"</th><th>"+team["disloyality"]+"</th><th>"+team["score"]+"</th></tr>";
                    for (i in team["players"]) {
                        player = team["players"][i];
                        if (player["name"] == user) {
                            divContents += "<tr style='color:#"+team["color"]+";'><td>"+player["name"]+"</td><td>"+player["spotCount"]+"</td><td>"+player["touchCount"]+"</td><td>"+player["disloyality"]+"</td><td>"+player["score"]+"</td></tr>";
                        }
                    }
                }
                divContents += "</table>";
                divContents += "<div class='bottom' id='toEnd'></div>";
                $("#stats").html(divContents);
            } else {
                $("#stats").html("");
            }
        });
    }
}



function getEvents() {
    if (document.getElementById("events")) {
        var divContents = "";
        $.ajax({
            url: "events.json?time="+Date.now()
        }).done(function(events) {
            if ("event" in events[0]) {
                console.log("No events to show");
                $("#events").html("");
            } else {
                for(i in events) {
                    event = events[i];
                    if (event["visible"] == "All" || (event["visible"] == "Sinised" && (userTeam % 2) == 1) || (event["visible"] == "Punased" && (userTeam % 2) == 0)) {
                        divContents += "<p>"+event["time"];
                        divContents += " <span style='color:#"+event["text1"]["color"]+";'>"+event["text1"]["text"]+"</span>";
                        divContents += " <span style='color:#"+event["text2"]["color"]+";'>"+event["text2"]["text"]+"</span>";
                        if (event["text3"]["text"] != null) {
                            divContents += " <span style='color:#"+event["text3"]["color"]+";'>"+event["text3"]["text"]+"</span>";
                        }
                        divContents += "</p>";
                    }
                }
                $("#events").html(divContents);
            }
        });
    }
}


function getRoundInfo() {
    if (document.getElementById("round-info")) {
        $.ajax({
            url: "stats.json?time="+Date.now()
        }).done(function(stats) {
            if(stats["roundName"] != null) {
                $("#round-info").html("<p>Lahing \"" + stats["roundName"] + "\", mängija: " + user + "</p>");
            } else {
                $("#round-info").html("");
            }
        });
    }
}


function timeToEnd() {
    currentDate = new Date();
    if (document.getElementById("round-info")) {
        $.ajax({
            url: "stats.json?time="+Date.now()
        }).done(function(stats) {
            if(stats["roundName"] != null) {
                var ending = stats["roundEnd"];
                endTime = new Date(ending.substring(0,4),ending.substring(5,7),ending.substring(8,10),ending.substring(11,13),ending.substring(14,16),ending.substring(17,19));
                var toEnd = new Date(endTime.getTime() - new Date(currentDate.getTime() + 21*60*60*1000));
                $("#toEnd").html("Aega vooru lõpuni " + addZerobefore(toEnd.getUTCHours()) + ":" + addZerobefore(toEnd.getUTCMinutes()) + ":" + addZerobefore(toEnd.getUTCSeconds()));
            } else {
                $("#toEnd").html("");
            }
        });
    }
}


function isJailed() {
    if (document.getElementById("isJailed")) {
        $.ajax({
            url: "isJailed"
        }).done(function(inJail) {
            userJailed = inJail;
        });
    }
}


function getUser() {
    $.ajax({
        url: "user"
    }).done(function(username) {
        user = username;
    });
}


function getUserTeam() {
    $.ajax({
        url: "userTeam"
    }).done(function(team) {
        userTeam = team;
    });
}


function getMessage() {
    $.ajax({
        url: "message"
    }).done(function(message) {
        if (message["message"] != null) {
            $("#messages").html(message["message"]);
        }
    });
}


function getBaseMessage() {
    $.ajax({
        url: "baseMessage"
    }).done(function(baseMessage) {
        if (!null) {
            $("#messages").html(baseMessage);
        }
    });
}


function addZerobefore(number) {
    if(parseInt(number) < 10 && parseInt(number) > -10) {
        number = "0" + parseInt(number);
    }
    return number;
}
