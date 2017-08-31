import itertools

from Phases import *
from Player import Player
from ruamel import yaml


class Game(object):

    logname = "werelog"

    END_PHASE = "END"

    def __init__(self, settings_file=None, players=None):

        """
        Create a new game with a specified list of players.

        A game always starts from the "SETUP" current_phase, in which,
        for example, the werewolves identify each other.
        Afterwards the normal game cycle begins.

        :param settings_file: str
            the YAML file with the game's settings.
        :param players: tuple(Player)
            the players that participate in the game.
            override player list from settings file.
            must be provided if no settings file was.
        """

        # import here to prevent circular dependencies

        # TODO: handle misuse of arguments (all None, etc.)

        self.logger = Game.init_log(Game.get_log_name())
        self.logger.info("Started Logging!")

        settings = yaml.safe_load(open(settings_file, 'r').read()) if settings_file else None
        self.players = players if players and len(players) > 0 else Player.create_players(settings['players'])
        self.alive_players = len(self.players)  # number of alive player
        self.alive_werewolves = sum(p.is_werewolf for p in self.players)  # number of alive werewolves
        self.current_phase = SetupPhase()
        self.phases = self._create_phases_generator((DayPhase(), NightPhase()))
        self.round = 0
        self.history = []
        self.in_progress = True

    def kill_player(self, player):

        """
        Kill a player.

        :param player: Player
            the player to kill
        """

        # TODO: also set whether the player was executed or eliminated (based on game's current phase)
        player.kill()
        self.alive_players -= 1
        if player.is_werewolf:
            self.alive_werewolves -= 1
        self.logger.info("{} was killed".format(player.name))

    def check_winning_conditions(self):

        """
        Check whether one of the winning conditions was achieved.

        :return: str
            "villagers" in case the villagers have won,
            "werewolves" in case the werewolves have won,
            None if no winning condition has been met.
        """

        # condition 1 - no more werewolves alive
        if self.alive_werewolves == 0:
            return "villagers"

        # condition 2 - equal number of villagers and werewolves
        if self.alive_werewolves == self.alive_players - self.alive_werewolves:
            return "werewolves"

        return None  # no winner yet

    @staticmethod
    def _create_phases_generator(phases):
        for phase in itertools.cycle(phases):
            yield phase

    def advance_phase(self):

        """
        Advance to the next phase of the game.

        If one of the winning conditions has met,
        the game will move to the END_PHASE, otherwise
        the game cycle will continue.

        """

        if self.in_progress:
            self.history.append(self.status_short())
            winner = self.check_winning_conditions()
            if winner:
                self.end_game(winner)
                self.current_phase = self.END_PHASE
            else:
                self.current_phase = next(self.phases)
                self.logger.debug(self.current_phase.announce())
                self.kill_player(self.current_phase.start(self))  # kill the elected player

    def get_history(self):
        return "\n".join(self.history)

    def end_game(self, winner):

        """
        End the game and announce the winner.

        :param winner: str
            the winning group of the game
        """

        self.in_progress = False
        self.logger.info("GAME ENDED\nThe {} won!\n".format(winner))
        self.logger.info("GameHistory\n" + self.get_history())

    def status(self):

        """
        Generate a YAML representation of the game's settings.

        :return: str
            a YAML representation of the game's settings
        """

        return \
            "players: {}\n".format(self.alive_players) + \
            "werewolves: {}\n".format(self.alive_werewolves) + \
            "villagers alive: {}\n".format(sum(not p.is_werewolf and p.is_alive for p in self.players)) + \
            "werewolves alive: {}\n".format(sum(p.is_werewolf and p.is_alive for p in self.players)) + \
            "phase: {}\n".format(self.current_phase)

    def status_all(self):

        """
        Generate a YAML representation of the game's info and status.

        :return: str
            a YAML representation of the game's info and status
        """

        # TODO: is there a way to directly serialize objects with ruamel?
        # game info
        status = "game:\n"
        for line in self.status().split("\n"):
            status += "  " + line + "\n"

        # player list
        status += "players:\n"
        for player in self.players:
            for line in player.status().split("\n"):
                status += "  " + line + "\n"

        return yaml.round_trip_load(status, preserve_quotes=True)

    def status_short(self):

        """
        Create a short string representation of the game's status.

        This representation includes the players' roles and state.

        :return: str
            a short string representation of the game's status
        """

        return "\t".join([p.status_short() for p in self.players])

    def get_alive_players(self):
        return [p for p in self.players if p.is_alive]

    @staticmethod
    def init_log(logname):
        logger = logging.getLogger(logname)
        handler = logging.NullHandler()
        formatter = logging.Formatter('%(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logging.basicConfig(filename=logname + ".log", level=logging.DEBUG)
        return logger

    @staticmethod
    def get_log_name():
        return Game.logname
