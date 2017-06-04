import random

class Game:
    started = False

    def __init__(self, config, cursor):
        self.config = config
        self.cursor = cursor

        # Create sites
        self.sites = {}
        for sitename in ['A', 'B', 'C']:
            self.sites[sitename] = Site(self, sitename)

        # Create teams
        self.teams = {}
        for teamname in ['CT', 'TR']:
            self.teams[teamname] = TeamNew(self, teamname)

        self.reset()

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


class TeamNew:
    ready = False

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def setReady(self, value):
        self.ready = value
        if self.parent.teams['CT'].ready and \
            self.parent.teams['TR'].ready:
            self.parent.start()


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
