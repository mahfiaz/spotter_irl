import psycopg2
import game_config

def connectDB():
    testConfigParams()
    database, host = (game_config.connection_dbname, game_config.connection_host)
    user, password = (game_config.connection_user, game_config.connection_password)
    connParams = "dbname='" + database + "' user='" + user + "' host='" + host + "' password='" + password + "'"
    try:
        connection = psycopg2.connect(connParams)
        return connection
    except:
        print ("Error. Unable to connect to the database. If losing data is acceptable, try running 'python reset_db.py'")
        return False

def testConfigParams():
    assert game_config.player_fleeingCodeDigits != game_config.code_spotCodeDigits
    assert game_config.code_touchCodeDigits != game_config.code_spotCodeDigits

def iterateZero(list):
    if list:
        return list[0]