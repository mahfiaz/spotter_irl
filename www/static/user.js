// GENERAL SETTINGS
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

// Polling
function poll() {
    setTimeout(function () {
        $.ajax({
            url: "/pollsite?site=" + bombsite,
            type: "GET",
            success: pollData,
            dataType: "json",
            complete: poll,
            timeout: 100
        });
    }, 500);
}

function pollData(data) {
    console.log(data);
    if (locked && !data['lock']) {
        unlock();
    }
    if (data['startround']) {
        startGame();
        return;
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
        if (armed)
            kaboom();
        else
            timerReached();
        clearInterval(beepTimer);
    }
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

// Finally start game
window.onload = function() {
    // Setup game
}


// Hit somebody
function hit() {
    $("#send").addEventListener("click", function() {
        $.ajax({
            url: /*TODO*/+$("#code").val()
        }).done(function(response) {
            $("#response").html(response);
        });
    })
}

// Get data from json to fill table contents
function getScoreTable() {
    var score = "";
    $.ajax({
        url: //TODO
    }).done(function(data) {
        for (var i in data["teams"]) {
            var team = data["teams"][i];
            score += "<div id='score-"+team["tag"]+"'>";
            score += "<table class='team-"+team["tag"]+"'>";
            score += "<thead><td width='20%'>"+team["tag"].toUpperCase()+"</td><td width='40%'>Player</td><td width='40%'>Hits</td></thead>";
            for (var j in team["players"]) {
                var player = team["players"][j];
                if (player["is_down"]) {
                    score += "<tr class='down'><td class='color'></td><td class='name'>"+player["name"]+"</td><td class='hits'>"+player["hits"]+"</td></tr>";
                } else {
                    score += "<tr><td class='color'></td><td class='name'>"+player["name"]+"</td><td class='hits'>"+player["hits"]+"</td></tr>";
                }
            }
            score += "</table></div>";
        }
        $(".scoretable").html(score);
    });
}