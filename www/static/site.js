// GENERAL SETTINGS
var debug = false;
var bombsite = 'A';
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

// Globals
var GET;
var round = 0;
var polling = false;

// Start round
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
    
    // Set bombsite characters
    $('.sitename').text(bombsite);

    // Set main image
    $('body').removeClass('site-a site-b');
    $('body').addClass('site-' + bombsite.toLowerCase());

    // Setup QR code
    var qrElement = document.getElementById("qrcode");
    qrcode = new QRCode(qrElement, {
        text: gameLink,
        width: 256,
        height: 256,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });

    // Load sounds
    initSounds(bombsite);

    // Unhide debug if necessary
    if (debug) {
        $('#lock-debug').removeClass('hidden');
    }

    if (!debug) {
        locked = true;
        gameOver = true;
        showOverlay('Game not yet started', '');
    }

    // Polling
    if (!polling) {
        poll();
        polling = true;
    }
}

function startGame() {
    winner = NaN;
    gameOver = false;
    clearOverlay();
    bombProgress(0, 'neutral');
    $('#timer-text').text('ROUND TIMER');

    // Start clock
    maxTime = roundLength;
    timerValue = maxTime + 1;
    startTimer();

    armed = false;
    disarmed = false;
    armingProgress = 0;
    disarmingProgress = 0;

    // Lock keypad
    lock();

    // Start music
    stop('background');
    play('wind');
}

function keypadFinished() {
    if (!armed) {
        // Arming
        armingProgress += 1;
        progress = armingProgress / armingSteps;
        if (progress > 0.99) {
            bombProgress(progress, 'armed');
            armingComplete();
        } else {
            bombProgress(progress, 'arming');
            delayLock();
        }
    } else {
        // Disarming
        disarmingProgress += 1;
        progress = disarmingProgress / disarmingSteps;
        if (progress > 0.99) {
            bombProgress(progress, 'disarmed');
            disarmingComplete();
        } else {
            bombProgress(progress, 'disarming');
            delayLock();
        }
    }
}

function armingComplete() {
    console.log('Arming complete');
    delayLock();
    armed = true;

    // Set timer to bomb timer
    $('#timer-text').text('BOMB TIMER');
    maxTime = bombTimer;
    timerValue = maxTime + 1;

    // TODO Send "Bomb has been planted" messages
    play('planted');
}

function disarmingComplete() {
    console.log('Disarming complete');
    play('defused');
    winner = 'CT';
    endGame();
}

function kaboom() {
    console.log('Kaboom');
    bombProgress(1, 'exploded');
    play('explosion');
    play('win-ct');
    winner = 'TR';
    endGame();
}

function timerReached() {
    console.log('Timer reached');
    winner = 'CT';
    play('win-ct');
    endGame();
}

function endGame() {
    stopTimer();
    locked = true;
    showOverlay(winner + ' won', '');
    stop('wind');
    //play('background');
    gameOver = true;
    round += 1;
}

// Polling
function poll() {
    setTimeout(function () {
        $.ajax({
            url: "/pollsite?site=" + bombsite,
            type: "GET",
            success: pollData,
            dataType: "json",
            complete: poll,
            timeout: 500
        });
    }, 1000);
}

function pollData(data) {
    if (locked && !data['lock']) {
        unlock();
    }
    if (data['events']) {
        for (var i = 0; i < data['events'].length; i++) {
            event = data['events'][i];
            console.log(event);
            if (event == 'started') {
                console.log('started');
                startGame();
            }
            if (event == 'reset') {
                console.log('resetted');
                endGame();
                initGame();
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

function blinkLed() {
    // Show LED
    $('#led').removeClass('hidden');
    // Hide LED
    window.setTimeout(function() {
        $('#led').addClass('hidden');
    }, 200);
}

var bombTexts = {
    'neutral': 'Not armed',
    'arming': 'Arming',
    'armed': 'Armed',
    'disarming': 'Disarming',
    'disarmed': 'Disarmed',
    'exploded': 'Exploded'
}

// Bomb bar
function bombProgress(progress, state) {
    // Act on completed stage.
    $('#bomb-progress-container').removeClass('neutral arming armed disarming disarmed');
    $('#bomb-progress-container').addClass(state);
    $('#message').text(bombTexts[state]);
    $('#bomb-progress').css('width', (progress * 100) + '%');
}

// Overlay messages
function showOverlay(message) {
    $('#overlay-message').text(message);
    $('#overlay').removeClass('notvisible');
}

function clearOverlay() {
    $('#overlay').addClass('notvisible');
}

// Keypad
var code = '';
var guessed = '';
var next = '';

function initCodepad(len) {
    code = randomCode(len);
    guessed = '';
    next = nextNumber();
    highlight(next);
    var d = '';
    for (var i = 0; i < len; i++) d += '-';
    $('#display').text(d);
    $('#display').removeClass('correct');
}

function randomCode(len) {
    var min = 10 ** (len - 1);
    var max = 10 ** len - 1;
    return '' + Math.floor(Math.random()*(max-min+1)+min);
}

function nextNumber() {
    for (var i = 0; i < code.length; i++) {
        if (i == guessed.length) {
            return code[i];
        }
    }
}

function highlight(number) {
    // First remove highlight
    $('.cp').removeClass('highlight');

    // Wait a little and mark a new key
    window.setTimeout(function() {
        $('#code'+number).addClass('highlight');
    }, 500);
}

function numberPressed(number) {
    if (locked) {
        flashLock();
        play('beep');
        return;
    }
    if (!armed) {
        progress = armingProgress / armingSteps;
        bombProgress(progress, 'arming');
    }
    if (armed) {
        progress = disarmingProgress / disarmingSteps;
        bombProgress(progress, 'disarming');
    }

    if (number == next) {
        guessed += number;

        // Set display
        var d = guessed;
        for (var i = d.length; i < code.length; i++) d += '-';
        $('#display').text(d);

        // Get next number
        next = nextNumber();
        highlight(next);

        if (guessed == code) {
            // Guessed full code
            d += '-OK'
            $('#display').text(d);
            $('#display').addClass('correct');

            keypadFinished();
            play('done');
        }
        else {
            play('press');
        }
    } else {
        // Wrong keypress
        play('beep');

        // Display ERROR
        $('#display').addClass('wrong');
        $('#display').text('YOLO');

        // Shake wrong key
        locked = true;
        $('#code' + number).addClass('shake');
        window.setTimeout(function () {
            $('#code' + number).removeClass('shake');
            $('#display').removeClass('wrong');
            // Make lock visible
            lock();
        }, 900);
    }
}

function lock() {
    // TODO get right QR code and regular code
    qrcode.clear();
    $.ajax('/getcode?site='+bombsite).done(lockCallback);
    locked = true;
    $('#lock').removeClass('notvisible');
}

function lockCallback(data) {
    unlockCode = data['code'];
    shortCode = data['shortcode'];
    var link = qrLink();
    qrcode.makeCode(link);
    $('#unlock-code').text(shortCode);
}

function delayLock() {
    window.setTimeout(lock, 1000);
}

function unlock() {
    locked = false;
    initCodepad(codeLength);
    $('#lock').addClass('notvisible');

    if (armed && !disarmingProgress) bombProgress(0, 'disarming');
}

function qrLink() {
    return link = 'http://' + gameLink + '/unlock?site=' + bombsite + '&code=' + unlockCode;
}

function flashLock() {
    $('#lock-image').addClass('shake');
    window.setTimeout(function () {
        $('#lock-image').removeClass('shake');
    }, 500);
}

// Sound bank
var sounds = {};

function initSounds(bombsite) {
    var folder = 'static/bombsite/'
    var suffix = bombsite + '.mp3'
    var s = sounds
    s['background'] = new Audio(folder + 'background.mp3');
    s['beep'] = new Audio(folder + 'beep.mp3');
    s['beep'].volume = 0.15;
    s['defused'] = new Audio(folder + 'defused.mp3');
    s['done'] = new Audio(folder + 'done.mp3');
    s['done'].volume = 0.5;
    s['explosion'] = new Audio(folder + 'explosion' + suffix);
    s['planted'] = new Audio(folder + 'planted.mp3');
    s['press'] = new Audio(folder + 'press.mp3');
    s['press'].volume = 0.6;
    s['win-ct'] = new Audio(folder + 'win-ct.mp3');
    s['win-tr'] = new Audio(folder + 'win-tr.mp3');
    s['wind'] = new Audio(folder + 'wind' + suffix);
    s['wind'].loop = true;
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

// Act on keypress
function keypress(e) {
    var key = e.which || e.keyCode;
    // Enter was pressed
    if (debug && key == 13) {
        if (gameOver) startGame();
        else if (locked) unlock();
        return;
    }

    // Ensure entered key is a number
    if(48 <= key && key <=57) {
        var number = parseInt(String.fromCharCode(key));
        numberPressed(number);
        return;
    }
    
    if (locked) flashLock();
    play('beep');
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
    bombsite = GET['site'];

    // Setup game
    initGame(bombsite);

    // Otherwise server starts game
    if (debug) startGame();

    // Register keypress listener
    window.addEventListener("keypress", keypress);
}
