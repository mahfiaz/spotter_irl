import random

class Code:

    def initOnce(cursor):
        Code.cur = cursor
        Code._createDataTable()

    def _createDataTable():
        Code.cur.execute("""CREATE TABLE code_list (
            code_id serial PRIMARY KEY,
            spot_code int unique,
            touch_code int unique,
            player_id int,
            added timestamp DEFAULT statement_timestamp())""")

    def _isValidSpotCodeFormat(code):
        return isinstance(code, int) and (code > 999 and code < 10000)

    def _isValidTouchCodeFormat(code):
        return isinstance(code, int) and (code > 99999 and code < 1000000)

    def getVictimIdByCode(code):
        if Code._isValidSpotCodeFormat(code):
            return Code._getSpotCodeOwnerId(code)
        if Code._isValidTouchCodeFormat(code):
            return Code._getTouchCodeOwnerId(code)

    def _getSpotCodeOwnerId(code):
        Code.cur.execute("""SELECT player_id
            FROM code_list
            WHERE spot_code = %s""", [code])
        return Code.cur.fetchone()

    def _getTouchCodeOwnerId(code):
        Code.cur.execute("""SELECT player_id
            FROM code_list
            WHERE touch_code = %s""", [code])
        return Code.cur.fetchone()


    def _getCodeIdByPlayerId(playerId):
        Code.cur.execute("""SELECT player_code_id
            FROM player_data
            WHERE player_id = %s""", [playerId])
        return Code.cur.fetchone()

    def _getSpotCodeId(code):
        Code.cur.execute("""SELECT code_id
            FROM code_list
            WHERE spot_code = %s""", [code])
        return Code.cur.fetchone()

    def getTouchCodeByPlayerId(playerId):
        codeId = Code._getCodeIdByPlayerId(playerId)
        code = Code._getTouchCodeById(codeId)
        if code:
            return code[0]

    def getSpotCodeByPlayerId(playerId):
        codeId = Code._getCodeIdByPlayerId(playerId)
        code = Code._getSpotCodeById(codeId)
        if code:
            return code[0]


    def _getSpotCodeById(spotId):
        Code.cur.execute("""SELECT spot_code
            FROM code_list
            WHERE code_id = %s""", [spotId])
        return Code.cur.fetchone()

    def _getTouchCodeById(touchId):
        Code.cur.execute("""SELECT touch_code
            FROM code_list
            WHERE code_id = %s""", [touchId])
        return Code.cur.fetchone()


    def generateNewCodes(playerId):
        spotCode = Code._generateSpotCode()
        touchCode = Code._generateTouchCode()
        Code.cur.execute("""INSERT INTO code_list (spot_code, touch_code, player_id)
            VALUES (%s, %s, %s)""", (spotCode, touchCode, playerId))
        codeId = Code._getSpotCodeId(spotCode)
        Code.cur.execute("""UPDATE player_data
            SET player_code_id = %s
            WHERE player_id = %s""", (codeId, playerId))
        return codeId

    def _generateSpotCode():
        fail = True
        while fail:
            newCode = random.randint(1000,9999)
            fail = Code._getSpotCodeOwnerId(newCode)
        return newCode

    def _generateTouchCode():
        fail = True
        while fail:
            newCode = random.randint(100000,999999)
            fail = Code._getTouchCodeOwnerId(newCode)
        return newCode


