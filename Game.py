from Cards import Cards, Type, Color
from Renderer import Renderer


class Game:
    def __init__(self, trump_color: Color, trump_types: list, cards: Cards, renderer: Renderer, players: list, rank: int):
        self.trump_color = trump_color
        self.trump_types = trump_types
        self.cards = cards
        self.renderer = renderer
        self.players = players
        self.played_cards = []

        self.trumps = [card for card in self.cards.deck if card.card_type in trump_types
                       or card.card_color == trump_color if card.card_color not in trump_types]

    @property
    def lead_card(self):
        if len(self.played_cards) != 0:
            return self.played_cards[0]
        else:
            return None

    def play_round(self):
        for player_num in range(len(self.players)):
            self.players[player_num].card_decision(renderer=self.renderer, lead_card=self.lead_card,
                                                   played_cards=self.played_cards, trumps=self.trumps)
        self.played_cards.clear()

    def play_game(self):
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round()


class Sauspiel(Game):
    def __init__(self, cards: Cards, renderer: Renderer, players: list):
        super().__init__(trump_color=Color.HERZ, trump_types=[Type.OBER, Type.UNTER], cards=cards, renderer=renderer, players=players, rank=1)

class Wenz(Game):
    def __init__(self, cards: Cards, renderer: Renderer, players: list):
        super().__init__(trump_color=Color.NOCOLOR, trump_types=[Type.UNTER], cards=cards, renderer=renderer, players=players, rank=3)

class Solo(Game):
    def __init__(self, trump_color: Color, cards: Cards, renderer: Renderer, players: list):
        super().__init__(trump_color=trump_color, trump_types=[Type.OBER, Type.UNTER], cards=cards, renderer=renderer, players=players, rank=4)