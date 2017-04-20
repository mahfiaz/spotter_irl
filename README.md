# spotter_irl
Spotting game intended to be played in real life with help of a printer and mobile phones.

## Server
/spotter_server

Python game server (keeping track of issued spotting numbers, players etc)


## Printer client
/spotter_printer

Python script which prepares a PDF and prints it out. Runs on Linux.

apt install inkscape qr


## SMS modem client
/spotter_sms

Python scripts which leverages smstools package to receive and send SMS messages.
Optional, the game can be played with web interface.

apt install smstools
