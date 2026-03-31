from Renderer import Renderer
from Cards import Cards
from handle_players import create_players, choose_starter, sort_players, play_game_decision, choose_game_decision
from card_dealing import prepare_cards


class Schafkopf:
    def __init__(self, renderer: Renderer):
        self.players = []
        self.starter = None
        self.game_choosers = []

        self.cards = Cards()
        self.renderer = renderer

    def main(self):
        self.players = create_players(renderer=self.renderer)
        self.starter = choose_starter(players=self.players)
        self.players = sort_players(players=self.players, starter=self.starter)
        self.cards.deck = prepare_cards(players=self.players, deck=self.cards.deck)
        for player in self.players:
            self.game_choosers = play_game_decision(player=player, renderer=self.renderer, game_choosers=self.game_choosers)
        if len(self.game_choosers) == 0:
            pass
        elif len(self.game_choosers) == 1:
            game_mode = choose_game_decision(renderer=self.renderer, player_name=self.game_choosers[0], cards=self.cards, players=self.players)
        else:
            game_mode = choose_game_decision(renderer=self.renderer, player_name=self.game_choosers[0],
                                             cards=self.cards, players=self.players)
        self.play_game()
        self.cards.reset_deck()