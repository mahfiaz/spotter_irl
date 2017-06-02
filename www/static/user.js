// GENERAL SETTINGS

var debug = true;
var bombsite = 'B';
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

// Sound bank
var sounds = {};

function initSounds(bombsite) {
    var folder = 'static/bombsite/'
    var suffix = bombsite + '.mp3'
    var s = sounds
    s['beep'] = new Audio(folder + 'beep.mp3');
    s['beep'].volume = 0.15;
    s['defused'] = new Audio(folder + 'defused.mp3');
    s['done'] = new Audio(folder + 'done.mp3');
    s['done'].volume = 0.5;
    s['planted'] = new Audio(folder + 'planted.mp3');
    s['press'] = new Audio(folder + 'press.mp3');
    s['press'].volume = 0.6;
    s['win-ct'] = new Audio(folder + 'win-ct.mp3');
    s['win-tr'] = new Audio(folder + 'win-tr.mp3');
}

function play(sound) {
    // Pause and time reset is to make sure
    // it restarts when still playing.
    sounds[sound].pause();
    sounds[sound].currentTime = 0;
    sounds[sound].play();
}

function stop(sound) {
    sounds[sound].pause();
    sounds[sound].currentTime = 0;
}

// Finally start game
window.onload = function() {
    // Setup game
}
