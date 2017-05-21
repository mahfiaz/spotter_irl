# -*- coding: utf-8 -*-

# database connection parameters
connection_dbname='game_database'
connection_user='game_engine'
connection_host='localhost'
connection_password='securityFirst'

database_dateformat = '%Y-%m-%d %H:%M:%S'
database_dateformat_hours_minutes = '%H:%M'

player_fleeingProtectionTime = 120

player_fleeingCodeDigits = 3
code_spotCodeDigits = 4
code_touchCodeDigits = 7

file_stats = 'stats.json'
file_events = 'events.json'

import datetime
round_day = datetime.datetime.now().date().strftime(database_dateformat[:8])
#round_day = '2017-05-27'
round_data = [
    {'name':'Soojendus',      'starts':'11:05', 'ends':'11:55'},
    {'name':'Ohtlik',       'starts':'12:05', 'ends':'12:55'},
    {'name':'Valus',        'starts':'13:05', 'ends':'13:55'},
    {'name':'Peamine',      'starts':'14:05', 'ends':'14:55'},
    {'name':'Kibe',         'starts':'15:05', 'ends':'15:55'},
    {'name':'Kriitiline',   'starts':'16:05', 'ends':'16:55'},
    {'name':'Karm',         'starts':'17:05', 'ends':'17:55'},
    {'name':'Viimane',      'starts':'18:05', 'ends':'18:55'}]


teams = ({'name':'Sinised', 'color':'3399FF'}, {'name':'Punased', 'color':'FF6699'})

master_player = {'name':'Master', 'mobile':'5254325'}

game_link_sms = 'http://fusiongame.tk'

def testConfigParams():
    assert player_fleeingCodeDigits != code_spotCodeDigits
    assert code_touchCodeDigits != code_spotCodeDigits

event_type_translated_Est = {'didFlee' : 'pages',
                'didSpot' : 'tabas',
                'didTouch' : 'puutus',
                'didSpotMate' : 'tabas',
                'wasAddedToTeam' : 'värvati',
                'teamChat' : 'teatas:'}

# for alert messages, like player X not added to any team.
game_master_mobile_number = '554433221'

event_type_translated = event_type_translated_Est

msgCellularEng = {}
msgCellularEng['notSignedUp'] = 'You ({}) have not been signed up for the game. Come to the base @ linnavalituses parkla.'
msgCellularEng['playerAdded'] = '{} welcome to jail. To escape, enter code {}.'
msgCellularEng['senderJailed'] = '{}, you are jailed and can not spot anybody. Escape jail with code {}.'
msgCellularEng['victimJailedVictim'] = '{}, if you were not jailed you would have been spotted by {}. Teleport quickly to the base with {}.'
msgCellularEng['victimJailedSender'] = '{}, if not jailed you would had spotted {}. If safe, tell {} to teleport to the base.'
msgCellularEng['missed'] = 'Hey {}, did you make up that code yourself? It was not found.'
msgCellularEng['oldCode'] = '{}, this code is old. Either have you good memory or {} is wearing old codes while having new ones.'
msgCellularEng['exposedSelf'] = '{}, you have exposed yourself to authorities. Did you mean selfie? Escape the jail with code {}.'
msgCellularEng['spotMateSender'] = '{}, are you colorblind? Hitting teammate {} is not OK.'
msgCellularEng['spotMateVictim'] = '{}, you have been spotted by a teammate. You can escape jail with code {}.'
msgCellularEng['spottedSender'] = '{}, you spotted {}. Good job!'
msgCellularEng['spottedVictim'] = '{}, you were spotted. Escape the jail with code {}.'
msgCellularEng['touchedSender'] = '{}, you touched {}. Excellent!'
msgCellularEng['touchedVictim'] = '{}, you were touched! Gotta be more watchful! Escape the jail with code {}.'
msgCellularEng['fleeingProtectionOver'] = '{}, your fleeing protection is over now, make the codes visible!'
msgCellularEng['noActiveRound'] = 'No running round. Next round starts at {}.'
msgCellularEng['roundStarted'] = '{} round just started!'
msgCellularEng['roundEnding'] = '{} round ends in {} minutes.'
msgCellularEng['roundEnded'] = '{} round ended. Come to the base and receive credits.'

msgBaseEng = {}
msgBaseEng['fleeingCodeMismatch'] = 'This code did not match. Try again or contact your lawyer!'
msgBaseEng['fledSuccessful'] = '{}, you managed to flee the jail! You have {} minutes of protection, when you are allowed to hide the code sheets!'
msgBaseEng['cantFleeFromLiberty'] = '{}, you are in freedom. Dont hang out at jail gates.'
msgBaseEng['playerNotUnique'] = '{} or {} or {} has been entered already! Try something else.'
msgBaseEng['playerAdded'] = '{}, welcome to the clan!'
msgBaseEng['roundStarted'] = '{} round just started!'
msgBaseEng['roundEnding'] = '{} round ends in {} minutes.'
msgBaseEng['roundEnded'] = '{} round ended.'
msgBaseEng['mobileNotDigits'] = 'Error. {} is not valid phone number. Start all over.'

msgCellularEst = {}
msgCellularEst['notSignedUp'] = '({}), sa pole mängu veel regatud. Tule Fusion telki @ linnavalituse parklas.'
msgCellularEst['playerAdded'] = '{}, sa oled vahistatud. Mine baasi ja kasuta koodi {}.'
msgCellularEst['senderJailed'] = '{}, oled vahistatud, seega ei saa kedagi tabada. Parem mine baasi ja kasuta koodi {}.'
msgCellularEst['victimJailedVictim'] = '{}, kui sa poleks vahistatud, oleks {} sind tabanud. Põgeneda saad baasis ruttu koodiga {}.'
msgCellularEst['victimJailedSender'] = '{}, kui {} poleks vahistatud, oleksid teda tabanud. Kui see on sulle turvaline, soovita tal põgeneda.'
msgCellularEst['missed'] = 'Kuule {}, mõtlesid selle koodi ise välja? Säänset ei leitud.'
msgCellularEst['oldCode'] = '{}, selle koodi parim-enne on möödas. Kas sul on hea mälu või {} kannab vana koodi, kuigi tal on juba uus käes.'
msgCellularEst['exposedSelf'] = '{}, andsid end ametivõimude kätte. Tegid enekat? Põgene baasis koodiga {}.'
msgCellularEst['spotMateSender'] = '{}, kas oled värvipime? {} on ikkagi tiimikaaslane.'
msgCellularEst['spotMateVictim'] = '{}, su meeskonnakaaslane lasi su üle. Põgenemise vihje {}.'
msgCellularEst['spottedSender'] = '{}, tabasid {}. Väga kõvv!'
msgCellularEst['spottedVictim'] = '{}, sind tabati. Põgenemiseks kasuta {}.'
msgCellularEst['touchedSender'] = '{}, sa lähitabasid võitlejat {}. Suurepärane!'
msgCellularEst['touchedVictim'] = '{}, sind lähitabati! Põgene koodiga {} ja ole ettevaatlikum.'
msgCellularEst['fleeingProtectionOver'] = '{}, su põgenemise kaitse on läbi, tee silt nähtavaks!'
msgCellularEst['noActiveRound'] = 'Lahing on läbi. Järgmine algab {}.'
msgCellularEst['roundStarted'] = '{} lahing just algas! Pane end valmis.'
msgCellularEst['roundEnding'] = '{} lahing lõpeb {} minuti pärast.'
msgCellularEst['roundEnded'] = '{} lahing on läbi. Baasis on auhindamine @ linnavalitsuse parkla.'

msgBaseEst = {}
msgBaseEst['fleeingCodeMismatch'] = 'See kood ei toiminud. Proovi mitte vigu sisse teha. Või kontakteeru oma juristiga.'
msgBaseEst['fledSuccessful'] = '{}, sul õnnestus kinnipidamisasutusest pageda! {} min jooksul võid neid koode peita!'
msgBaseEst['cantFleeFromLiberty'] = '{}, sa ju oled vaba!? Ära hängi kongi väravate ümbruses.'
msgBaseEst['playerAdded'] = '{}, teretulemast-toretelemast sellesse põnevasse lahingusse!'
msgBaseEst['playerNotUnique'] = '{} või {} või {} on kellegi poolt juba sisestatud! Proovi millegi muuga.'
msgBaseEst['roundStarted'] = '{} lahing algas!'
msgBaseEst['roundEnding'] = '{} lõpeb {} minuti pärast.'
msgBaseEst['roundEnded'] = '{} lahing on läbi.'
msgBaseEst['mobileNotDigits'] = 'Viga. {} pole ju telefoni number. Alusta uuesti.'

msgCellular = msgCellularEst
msgBase = msgBaseEst
