
# database connection parameters
connection_dbname='game_database'
connection_user='game_engine'
connection_host='localhost'
connection_password='securityFirst'

database_dateformat = '%Y-%m-%d %H:%M:%S'

player_fleeingProtectionTime = 2 #120

player_fleeingCodeDigits = 3
code_spotCodeDigits = 4
code_touchCodeDigits = 7

team_names = ('Sinised', 'Punased')

def testConfigParams():
    assert player_fleeingCodeDigits != code_spotCodeDigits
    assert code_touchCodeDigits != code_spotCodeDigits

