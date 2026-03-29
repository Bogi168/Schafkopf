from Cards import Cards
from card_dealing import *
from create_players import *

class Game:
    def __init__(self):
        self.players = []
        self.played_cards = []
        self.cards_ranking = ()

        self.cards = Cards()

    def play_round(self):
        self.cards.reset_deck()
        self.players = create_players()
        deal_cards(cards = self.cards.deck, players = self.players)