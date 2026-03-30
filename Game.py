from Cards import Cards, Type
from Renderer import Renderer
from card_dealing import *
from handle_players import create_players, choose_starter, sort_players

class Game:
    def __init__(self, renderer: Renderer):
        self.players = []
        self.trumps = []
        self.starting_order = []
        self.played_cards = []
        self.cards_ranking = ()

        self.cards = Cards()
        self.renderer = renderer

    @property
    def lead_card(self):
        if len(self.played_cards) != 0:
            return self.played_cards[0]
        else:
            return None

    def prepare_cards(self):
        self.cards.reset_deck()
        for player in self.players:
            player.player_cards.clear()
            player.collected_cards.clear()
        deal_cards(deck= self.cards.deck, players = self.players, trumps=self.trumps)

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
        for rounds in range(1,5):
            self.play_round()

    def main(self):
        self.players = create_players(renderer=self.renderer)
        choose_starter(players=self.players)
        self.play_game()

class Sauspiel(Game):
    def __init__(self, renderer):
        super().__init__(renderer=renderer)
        self.trumps = [trump for trump in self.cards.full_deck if trump.card_type in (Type.OBER, Type.UNTER)
                       or trump.card_color == Color.HERZ]