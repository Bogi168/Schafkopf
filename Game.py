from Cards import Cards
from Renderer import Renderer
from card_dealing import *
from create_players import *
import random


def choose_starter(players: list):
    starter = random.choice(players)
    starter.bool_beginner = True
    return starter.player_name

def sort_players(players: list):
    found_winner = False
    while not found_winner:
        player = players.__getitem__(0)
        if not player.bool_beginner:
                players.append(player)
                players.pop(0)
        else:
            found_winner = True
    return players

class Game:
    def __init__(self, renderer: Renderer):
        self.players = []
        self.starting_order = []
        self.played_cards = []
        self.cards_ranking = ()

        self.cards = Cards()
        self.renderer = renderer

    def prepare_cards(self):
        self.cards.reset_deck()
        for player in self.players:
            player.player_cards.clear()
        deal_cards(cards = self.cards.deck, players = self.players)

    def prepare_players(self):
        self.starting_order = sort_players(self.players)
        self.players = self.starting_order.copy()

    def play_round(self):
        for player_num in range(len(self.players)):
            self.players[player_num].decision()


    def play_game(self):
        self.players = create_players()
        choose_starter(players=self.players)
        self.prepare_players()
        self.play_round()