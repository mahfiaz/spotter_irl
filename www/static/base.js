// GENERAL SETTINGS
var team = 'CT';

var roundLength = 1.5 * 60;
var bombTimer = 30;
var codeLength = 4; // chars
var armingSteps = 3;
var disarmingSteps = 2;

var gameLink = 'http://game.pll.ee/';
var unlockCode = 123456;

// Game variables
var armed, disarmed;
var armingProgress, disarmingProgress;
var locked = true;
var winner = NaN;
var gameOver = false;
var qrcode = NaN;
var teamready = false;

function initGame(site) {
    if (site) {
        bombsite = site;
    }

    $.ajax('sitesettings').done(initEnd);
}

function initEnd(data) {
    roundLength = parseInt(data['roundlength']);
    bombTimer = parseInt(data['bombtimer']);
    armingSteps = parseInt(data['armingsteps']);
    disarmingSteps = parseInt(data['disarmingsteps']);
    gameLink = data['link'];
}

// Polling
function poll() {
    setTimeout(function () {
        $.ajax({
            url: "/pollsite?site=" + team,
            type: "GET",
            success: pollData,
            dataType: "json",
            complete: poll,
            timeout: 100
        });
    }, 500);
}

function pollData(data) {
    //console.log(data);
    if (locked && !data['lock']) {
        unlock();
    }
    if (data['events']) {
        for (var i = 0; i < data['events'].length; i++) {
            event = data['events'][i];
            eventname = event[0];
            eventdata = event[1];

            console.log(eventname);
            if (eventname == 'started') {
                maxTime = roundLength;
                timerValue =  maxTime + 1;
                startTimer();
                $('#timer-text').text('ROUND TIMER');
            }
            if (eventname == 'reset') {
                window.location = window.location;
            }
            if (eventname == 'planted' && eventdata['origin'] != bombsite) {
                play('planted');
                maxTime = bombTimer;
                timerValue = maxTime + 1;
                $('#timer-text').text('BOMB TIMER');
            }
            if (eventname == 'ended' && eventdata['origin'] != bombsite) {
                winner = eventdata['winner'];
                console.log(winner);
                $('#timer-text').text(winner + 'WON');
            }
        }
    }
}



// Timer
var maxTime = roundLength;
var timerValue = maxTime + 1;
var beepTimer;
var odd = true;

function startTimer() {
    beepTimer = setInterval(timer, 500);
    odd = false;
    timer();
}

function stopTimer() {
    clearInterval(beepTimer);
}

function timer() {
    odd = !odd;
    if (odd) {
        // Every second time do not run full timer.
        if (armed && timerValue <= 10)
            play('beep');
        return;
    }
    else {
        if (armed) play('beep');
    }

    // Change time
    timerValue -= 1;
    advanceClock();
    if (armed) blinkLed();

    // Kaboom
    if (timerValue == 0) {
        if (armed) {
            //kaboom();
        } else {
            timerReached();
        }
        clearInterval(beepTimer);
    }
}

function timerReached() {
    stopTimer();
}

function advanceClock() {
    // Set countdown clock
    var minutes = Math.floor(timerValue / 60);
    var seconds = timerValue - (minutes * 60);
    if (seconds < 10) seconds = '0' + seconds;
    $('#timer-minutes').text(minutes);
    $('#timer-seconds').text(seconds);
    // Set progress bar
    var width = 100 * ((maxTime - timerValue) / maxTime);
    $('#progressbar').css('width', width + '%');
}

// Overlay messages
function showOverlay(message) {
    $('#overlay-message').text(message);
    $('#overlay').removeClass('notvisible');
}

function clearOverlay() {
    $('#overlay').addClass('notvisible');
}

// Add user
function addUser() {
    $("#ct").click(function() {team = "CT";console.log("CTd");});
    $("#tr").click(function() {team = "TR";console.log("TRd");});
    $("input[name=send]").click(function() {
        console.log("Registered");
        console.log($("input[name=username]").val());
        console.log($("input[name=mobile]").val());
        $.ajax({
            url: "ap?username="+$("input[name=username]").val()+"&phone="+$("input[name=mobile]").val()+"&team="+team
        }).done(function(response) {
            $("#response").html(response);
        });
    })
}

// Eventlist
function getEvents() {
    var events = "";
    $.ajax({
        url: "/"//TODO
    }).done(function(data) {
        for (var i in data["events"]) {
            var event = data["events"][i];
            if (event["type"] == "personal") {
                events += "<p>"+event["time"]+" "+event["commiter"]+" "+event["event"]+" "+event["target"]+"</p>";
            } else {
                events += "<p>"+event["time"]+" "+event["event"]+"</p>";
            }
        }
        $(".eventlist").html(events);
    });
}

// Get query parameters
function getQueryParams(qs) {
    qs = qs.split("+").join(" ");
    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])]
            = decodeURIComponent(tokens[2]);
    }

    return params;
}

// Finally start game
window.onload = function() {
    GET = getQueryParams(document.location.search);
    team = GET['team'];
    
    initGame();
    
    // Setup game
    addUser();
    getEvents();
    var allEvents = setInterval(function() {
        getEvents();
    }, 2000);
    $('#readybutton').click(function () {
        teamready = !teamready;
        $.ajax('teamready?team='+team+'&state='+teamready)
            .done(function () {
                console.log(teamready);
                if (teamready) {
                    $('#readybutton').addClass('green').removeClass('gray');
                } else {
                    $('#readybutton').removeClass('green').addClass('gray');
                }
            });
    });
    
    poll();
}
