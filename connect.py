import psycopg2
import game_config

def connectDB():
    game_config.testConfigParams()
    database, host = (game_config.connection_dbname, game_config.connection_host)
    user, password = (game_config.connection_user, game_config.connection_password)
    connParams = "dbname='" + database + "' user='" + user + "' host='" + host + "' password='" + password + "'"
    try:
        connection = psycopg2.connect(connParams)
        connection.set_session(autocommit=True)
        return connection
    except:
        print ("Error. Unable to connect to the database. If losing data is acceptable, try running 'python reset_db.py'")
        return False
