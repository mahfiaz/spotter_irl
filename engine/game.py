from .code import Codes
from .player import Player, Players
from .round import Round, Rounds
from .team import Team, Teams

import logging
import random

class Game:
    started = False

    def __init__(self, config, log, cursor, sms_queue, printer_queue):
        self.config = config
        self.log = log
        self.cur = cursor

        # Init database?
        Game.init_database(cursor)

        self.codes = Codes(self)

        # Create sites
        self.sites = {}
        for sitename in ['A', 'B', 'C']:
            self.sites[sitename] = Site(self, sitename)

        # Create round
        self.rounds = Rounds(self)
        #self.rounds.new()

        # Create teams
        self.teams = Teams(self)

        # Create players
        self.players = Players(self)
        self.players.load_all()

        # Testing

        self.reset()

    def init_database(cursor):
        Codes.init_database(cursor)
        Players.init_database(cursor)
        Teams.init_database(cursor)
        Rounds.init_database(cursor)

    def reset(self):
        self.sendall('reset')

    def start(self):
        self.started = True
        self.sendall('started')

    def planted(self, origin):
        self.started = True
        self.sendall('planted', {'origin': origin})

    def ended(self, origin, winner):
        self.started = True
        self.sendall('ended', {'origin': origin, 'winner': winner})

    def sendall(self, message, data = {}):
        for name in self.sites:
            site = self.sites[name]
            site.events.append([message, data])


class Site:
    locked = True
    code = None
    shortcode = None

    starting = False

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.lock()
        self.events = []

    def lock(self):
        self.locked = True
        self.code = self.generate_code(7)
        self.shortcode = self.generate_code(3)
        return (self.code, self.shortcode)

    def unlock(self, code):
        if str(code) == str(self.code) \
            or str(code) == str(self.shortcode):
            self.locked = False
            return 'Site %s unlocked' % self.name
        else:
            return 'Code not correct'

    def generate_code(self, length):
        min_num = 10 ** (length - 1) + 1
        max_num = 10 ** length - 1
        # Ensure it's odd for A and even for B
        while True:
            code = random.randint(min_num, max_num)
            if self.name == 'A' and (code % 2) == 1:
                break
            elif self.name == 'B' and (code % 2) == 0:
                break
            elif self.name not in ['A', 'B']:
                # Don't care
                break
        return code
