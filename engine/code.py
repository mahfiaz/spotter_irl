import random


class Codes:
    def __init__(self, parent):
        self.parent = parent
        self.log = parent.log
        self.cur = parent.cur

    def init_database(cursor):
        cursor.execute("""DROP TABLE IF EXISTS codes""")
        cursor.execute("""CREATE TABLE codes (
            cid serial PRIMARY KEY,
            spot_code int unique,
            touch_code int unique,
            pid int,
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

    def _isActiveCode(playerId, codeId):
        otherCodeId = Code._getCodeIdByPlayerId(playerId)
        assert type(codeId) == type(otherCodeId)
        return otherCodeId == codeId

    def generate_codes(self, player):
        spot_code = self.spotcode()
        touch_code = self.touchcode()
        self.cur.execute("""INSERT INTO code
            (spot_code, touch_code, pid)
            VALUES (%s, %s, %s) RETURNING cid""",
            (spotCode, touchCode, playerId))
        code_id = self.cur.fetchone()[0]
        self.cur.execute("""UPDATE players
            SET cid = %s WHERE pid = %s""",
            (code_id, player.id))

    def spotcode(self):
        length = self.parent.config['code']['spot_code_length']
        return self.generate_code(length)

    def touchcode(self):
        length = self.parent.config['code']['touch_code_length']
        return self.generate_code(length)

    def generate_code(self, length = 5):
        min_code = 10 ** (length - 1)
        max_code = 10 ** length - 1
        while True:
            code = random.randint(min_code, max_code)
            # Ensure it's unique
            if True:
                return code
