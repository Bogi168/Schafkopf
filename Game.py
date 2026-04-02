from abc import ABC, abstractmethod
from Cards import Cards, Type, Color
from Renderer import Renderer
from handle_cards import adjust_rank, find_strongest_card


class Game(ABC):
    rank = 0
    def __init__(self, trump_color: Color, trump_types: list, cards: Cards, renderer: Renderer, players: list, sau_color = None):
        self.trump_color = trump_color
        self.trump_types = trump_types
        self.cards = cards
        self.renderer = renderer
        self.players = players
        self.sau_color = sau_color

        # lists
        self.played_cards = []
        self.team_1 = []
        self.team_2 = []
        self.team_3 = []
        self.team_4 = []
        self.teams = [self.team_1, self.team_2, self.team_3, self.team_4]
        self.trumps = [card for card in self.cards.full_deck if card.card_type in trump_types
                       or card.card_color == trump_color]

    @property
    def call_sau(self):
        call_sau = None
        for player in self.players:
            for card in player.player_cards:
                if card.card_color == self.sau_color and card.card_type == Type.SAU:
                    call_sau = card
        return call_sau

    @property
    def lead_card(self):
        if len(self.played_cards) != 0:
            return self.played_cards[0]
        else:
            return None

    @abstractmethod
    def create_teams(self):
        pass

    def sort_players(self, starter):
        found_beginner = False
        while not found_beginner:
            player = self.players.__getitem__(0)
            if not player == starter:
                self.players.append(player)
                self.players.pop(0)
            else:
                found_beginner = True

    def play_round(self):
        for player in self.players:
            player.card_decision(game_mode=self, renderer=self.renderer, lead_card=self.lead_card,
                                 played_cards=self.played_cards, trumps=self.trumps, call_sau=self.call_sau)
        strongest_card = find_strongest_card(played_cards=self.played_cards, trumps=self.trumps)
        winner_index = self.played_cards.index(strongest_card)
        for card in self.played_cards:
            self.players[winner_index].collected_cards.append(card)
        starter = self.players[winner_index]
        self.sort_players(starter=starter)
        for player in self.players:
            print(f"{player.player_name} has collected {player.collected_cards}")
        self.played_cards.clear()

    def play_game(self, chooser):
        for player in self.players:
            player.player_cards = adjust_rank(player_cards=player.player_cards, trumps=self.trumps)
            player.player_cards.sort(key=lambda sort_card: sort_card.card_rank, reverse=True)
        self.team_1.append(chooser)
        self.create_teams()
        print(f"Team 1: {self.team_1}")
        print(f"Team 2: {self.team_2}")
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round()


class Sauspiel(Game):
    rank = 1
    def __init__(self, cards: Cards, renderer: Renderer, players: list, sau_color: Color):
        super().__init__(trump_color=Color.HERZ, trump_types=[Type.OBER, Type.UNTER], cards=cards, renderer=renderer, players=players, sau_color = sau_color)

    def create_teams(self):
        self.teams.remove(self.team_3)
        self.teams.remove(self.team_4)
        for player in self.players:
            for card in player.player_cards:
                if card == self.call_sau:
                    self.team_1.append(player)
        self.team_2 = [player for player in self.players if player not in self.team_1]


class Wenz(Game):
    rank = 2
    def __init__(self, cards: Cards, renderer: Renderer, players: list):
        super().__init__(trump_color=None, trump_types=[Type.UNTER], cards=cards, renderer=renderer, players=players)

    def create_teams(self):
        self.teams.remove(self.team_3)
        self.teams.remove(self.team_4)
        self.team_2 = [player for player in self.players if player not in self.team_1]


class Solo(Game):
    rank = 3
    def __init__(self, trump_color: Color, cards: Cards, renderer: Renderer, players: list):
        super().__init__(trump_color=trump_color, trump_types=[Type.OBER, Type.UNTER], cards=cards, renderer=renderer, players=players)

    def create_teams(self):
        self.teams.remove(self.team_3)
        self.teams.remove(self.team_4)
        self.team_2 = [player for player in self.players if player not in self.team_1]