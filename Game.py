from Cards import Cards, Type, Color
from Renderer import Renderer
from card_dealing import adjust_rank


class Game:
    rank = 0
    def __init__(self, trump_color: Color, trump_types: list, cards: Cards, renderer: Renderer, players: list):
        self.trump_color = trump_color
        self.trump_types = trump_types
        self.cards = cards
        self.renderer = renderer
        self.players = players
        self.played_cards = []

        self.trumps = [card for card in self.cards.full_deck if card.card_type in trump_types
                       or card.card_color == trump_color]

    @property
    def lead_card(self):
        if len(self.played_cards) != 0:
            return self.played_cards[0]
        else:
            return None

    def play_round(self):
        for player_num in range(len(self.players)):
            self.players[player_num].card_decision(game_mode=self, renderer=self.renderer, lead_card=self.lead_card,
                                                   played_cards=self.played_cards, trumps=self.trumps, call_sau=None)
        self.played_cards.clear()

    def play_game(self):
        for player in self.players:
            player.player_cards = adjust_rank(player_cards=player.player_cards, trumps=self.trumps)
            player.player_cards.sort(key=lambda sort_card: sort_card.card_rank, reverse=True)
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round()


class Sauspiel(Game):
    rank = 1
    def __init__(self, cards: Cards, renderer: Renderer, players: list, sau_color: Color):
        super().__init__(trump_color=Color.HERZ, trump_types=[Type.OBER, Type.UNTER], cards=cards, renderer=renderer, players=players)
        self.sau_color = sau_color

    @property
    def call_sau(self):
        call_sau = None
        for player in self.players:
            for card in player.player_cards:
                if card.card_color == self.sau_color and card.card_type == Type.SAU:
                    call_sau = card
        return call_sau

    def play_round(self):
        for player_num in range(len(self.players)):
            self.players[player_num].card_decision(game_mode=self, renderer=self.renderer, lead_card=self.lead_card,
                                                   played_cards=self.played_cards, trumps=self.trumps, call_sau=self.call_sau)
        self.played_cards.clear()

class Wenz(Game):
    rank = 2
    def __init__(self, cards: Cards, renderer: Renderer, players: list):
        super().__init__(trump_color=None, trump_types=[Type.UNTER], cards=cards, renderer=renderer, players=players)

class Solo(Game):
    rank = 3
    def __init__(self, trump_color: Color, cards: Cards, renderer: Renderer, players: list):
        super().__init__(trump_color=trump_color, trump_types=[Type.OBER, Type.UNTER], cards=cards, renderer=renderer, players=players)