import math
import random

import game_config
from .helper import iterateZero

class Code:

# init
    def initDB(cursor):
        Code.cur = cursor
        Code._createDataTable()

    def initConnect(cursor):
        Code.cur = cursor

    def _createDataTable():
        Code.cur.execute("""DROP TABLE IF EXISTS code_list""")
        Code.cur.execute("""CREATE TABLE code_list (
            code_id serial PRIMARY KEY,
            spot_code int unique,
            touch_code int unique,
            player_id int,
            added timestamp DEFAULT statement_timestamp())""")

# gets
    def getVictimIdByCode(code):
        result = None
        if Code._isValidSpotCodeFormat(code):
            result = Code._getSpotCodeOwnerId(code)
        if Code._isValidTouchCodeFormat(code):
            result = Code._getTouchCodeOwnerId(code)
        if result:
            playerId, codeId = result
            return playerId, Code._isActiveCode(playerId, codeId)
        return None, None

    def getTouchCodeByPlayerId(playerId):
        codeId = Code._getCodeIdByPlayerId(playerId)
        return Code._getTouchCodeById(codeId)

    def getSpotCodeByPlayerId(playerId):
        codeId = Code._getCodeIdByPlayerId(playerId)
        return Code._getSpotCodeById(codeId)

# internals
    def _isValidSpotCodeFormat(code):
        codeMax = math.pow(10, game_config.code_spotCodeDigits)
        assert isinstance(code, int)
        return (code > (codeMax / 10) and code < (codeMax - 1))

    def _isValidTouchCodeFormat(code):
        codeMax = math.pow(10, game_config.code_touchCodeDigits)
        return isinstance(code, int) and (code > (codeMax / 10) and code < (codeMax - 1))

    def _getSpotCodeOwnerId(code):
        Code.cur.execute("""SELECT player_id, code_id
            FROM code_list
            WHERE spot_code = %s""", [code])
        return Code.cur.fetchone()

    def _getTouchCodeOwnerId(code):
        Code.cur.execute("""SELECT player_id, code_id
            FROM code_list
            WHERE touch_code = %s""", [code])
        return Code.cur.fetchone()

    def _isActiveCode(playerId, codeId):
        otherCodeId = Code._getCodeIdByPlayerId(playerId)
        assert type(codeId) == type(otherCodeId)
        return otherCodeId == codeId

    def _getCodeIdByPlayerId(playerId):
        Code.cur.execute("""SELECT player_code_id
            FROM player_data
            WHERE player_id = %s""", [playerId])
        return iterateZero(Code.cur.fetchone())

    def _getSpotCodeId(code):
        Code.cur.execute("""SELECT code_id
            FROM code_list
            WHERE spot_code = %s""", [code])
        return iterateZero(Code.cur.fetchone())

    def _getSpotCodeById(spotId):
        Code.cur.execute("""SELECT spot_code
            FROM code_list
            WHERE code_id = %s""", [spotId])
        return iterateZero(Code.cur.fetchone())

    def _getTouchCodeById(touchId):
        Code.cur.execute("""SELECT touch_code
            FROM code_list
            WHERE code_id = %s""", [touchId])
        return iterateZero(Code.cur.fetchone())

# generate
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
        codeMax = math.pow(10, game_config.code_spotCodeDigits)
        fail = True
        while fail:
            newCode = random.randint(codeMax / 10, codeMax - 1)
            fail = Code._getSpotCodeOwnerId(newCode)
        return newCode

    def _generateTouchCode():
        codeMax = math.pow(10, game_config.code_touchCodeDigits)
        fail = True
        while fail:
            newCode = random.randint(codeMax / 10, codeMax - 1)
            fail = Code._getTouchCodeOwnerId(newCode)
        return newCode


