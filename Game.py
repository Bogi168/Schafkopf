from Cards import Cards
from Renderer import Renderer
from card_dealing import *
from handle_players import create_players, choose_starter, sort_players

class Game:
    def __init__(self, renderer: Renderer):
        self.players = []
        self.starting_order = []
        self.played_cards = []
        self.cards_ranking = ()

        self.cards = Cards()
        self.renderer = renderer

    @property
    def first_card(self):
        if len(self.played_cards) == 0:
            return self.played_cards[0]
        else:
            return None

    def prepare_cards(self):
        self.cards.reset_deck()
        for player in self.players:
            player.player_cards.clear()
            player.collected_cards.clear()
        deal_cards(cards = self.cards.deck, players = self.players)

    def prepare_players(self):
        self.starting_order = sort_players(self.players)
        self.players = self.starting_order.copy()

    def play_round(self):
        for player_num in range(len(self.players)):
            self.players[player_num].decision()


    def play_game(self):
        self.players = create_players(renderer = self.renderer)
        choose_starter(players = self.players)
        self.prepare_players()
        self.prepare_cards()
        self.play_round()