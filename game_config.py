# -*- coding: utf-8 -*-
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

language = ConfigParser()
language.read(config['general']['languagefile'])

# database connection parameters
db = config['database']
connection_host = db['host']
connection_dbname = db['dbname']
connection_user = db['user']
connection_password = db['password']

database_dateformat = config['date']['format']
database_dateformat_hours_minutes = config['date']['shortformat']

player_fleeingProtectionTime = config['game']['flee_protection']
player_fleeingCodeDigits = int(config['game']['flee_code_length'])
code_spotCodeDigits = int(config['game']['spot_code_length'])
code_touchCodeDigits = int(config['game']['touch_code_length'])

file_stats = config['general']['stats_file']
file_events = config['general']['events_file']

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

master_player = {'name':'Master', 'mobile': config['general']['phone_alert']}

game_link_sms = config['game']['link']

def testConfigParams():
    assert player_fleeingCodeDigits != code_spotCodeDigits
    assert code_touchCodeDigits != code_spotCodeDigits

# for alert messages, like player X not added to any team.
game_master_mobile_number = config['general']['phone_alert']

event_type_translated = language['events']
msgCellular = language['sms']
msgBase = language['messages']
