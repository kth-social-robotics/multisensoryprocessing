import logging

from abc import ABCMeta
from abc import abstractmethod
from random import choice
from collections import Counter


class AbstractPhase(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        from Game import Game
        self.name = "None"
        self.logger = logging.getLogger(Game.logname)

    def announce(self):
        return "{} phase started".format(self.name)

    @abstractmethod
    def start(self, game):
        raise NotImplementedError("use this function with one of the phases")


class SetupPhase(AbstractPhase):

    def __init__(self):
        super(SetupPhase, self).__init__()
        self.name = "Setup"

    def start(self, game):
        # TODO: werewolves see each other. anything else?
        pass


class DayPhase(AbstractPhase):

    def __init__(self):
        super(DayPhase, self).__init__()
        self.name = "Day"

    def start(self, game):
        # TODO: discussion part
        # TODO: accusation part

        # Execution part
        return self._vote_to_execute(game.get_alive_players())

    def _vote_to_execute(self, alive_players):

        """
        Pick a player (villager or werewolf) to kill

        In case of tie(s), continue voting till there is
        a single player with the highest number of votes.
        The actual voting is performed by Player.vote(),
        see _collect_votes() for more details.

        :param alive_players: list(Player)
            the players in the game that are still alive
            (and therefore are allowed to vote).
        :return: Player
            the player that was chosen to be killed
        """

        # start with all the players alive can be executed
        kill_targets = list(alive_players)
        while len(kill_targets) != 1:
            # collect player votes
            votes = {p: p.vote(kill_targets) for p in alive_players}
            # count the votes and get highest voting score
            counts = Counter(votes.values())
            _, most_votes = counts.most_common(1)[0]
            # gather all players that got the highest number of voting
            kill_targets = [k for k, v in counts.iteritems() if v == most_votes]
        return kill_targets[0]


class NightPhase(AbstractPhase):

    def __init__(self):
        super(NightPhase, self).__init__()
        self.name = "Night"

    def start(self, game):
        # TODO: elimination part

        # choose a random alive villager
        return choice([p for p in game.get_alive_players() if not p.is_werewolf])

    @staticmethod
    def _collect_votes(alive_players):
        return {p: p.vote(alive_players) for p in alive_players}
