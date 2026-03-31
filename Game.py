from Cards import Cards, Type
from Renderer import Renderer
from card_dealing import *
from handle_players import create_players, choose_starter, sort_players


class Game:
    def __init__(self, renderer: Renderer, trump_color, trump_types):
        self.trump_color = trump_color
        self.trump_types = trump_types
        self.players = []
        self.trumps = []
        self.starting_order = []
        self.played_cards = []
        self.cards_ranking = ()

        self.cards = Cards()
        self.renderer = renderer

        self.trumps = [card for card in self.cards.deck if card.card_type in trump_types
                       or card.card_color == trump_color if card.card_color not in trump_types]

    @property
    def lead_card(self):
        if len(self.played_cards) != 0:
            return self.played_cards[0]
        else:
            return None

    def prepare_cards(self):
        for player in self.players:
            player.player_cards.clear()
            player.collected_cards.clear()
        self.cards.deck = deal_cards(deck=self.cards.deck, players=self.players, trumps=self.trumps)

    def prepare_players(self):
        self.starting_order = sort_players(self.players)
        self.players = self.starting_order.copy()

    def play_round(self):
        for player_num in range(len(self.players)):
            self.players[player_num].decision(renderer=self.renderer, lead_card=self.lead_card,
                                              played_cards=self.played_cards, trumps=self.trumps)
        self.played_cards.clear()

    def play_game(self):
        self.prepare_players()
        self.prepare_cards()
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round()
        self.cards.reset_deck()

    def main(self):
        print(self.trumps)
        self.players = create_players(renderer=self.renderer)
        choose_starter(players=self.players)
        self.play_game()

class Sauspiel(Game):
    def __init__(self, renderer):
        super().__init__(renderer=renderer, trump_color=Color.HERZ, trump_types=(Type.OBER, Type.UNTER))

class Solo(Game):
    def __init__(self, renderer, trump_color, trump_types):
        super().__init__(renderer=renderer, trump_color=trump_color, trump_types=trump_types)