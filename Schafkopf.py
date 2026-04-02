from Renderer import Renderer
from Cards import Cards
from Game import Sauspiel, Wenz, Solo
from handle_players import create_players, choose_starter, sort_players, play_game_decision, players_choose_game
from handle_cards import prepare_cards


class Schafkopf:
    def __init__(self, renderer: Renderer):
        self.playable_games = [Sauspiel, Wenz, Solo]
        self.players = []
        self.starter = None
        self.game_choosers = []
        self.game_mode = None

        self.cards = Cards()
        self.renderer = renderer

    def main(self):
        self.players = create_players(renderer=self.renderer)
        self.starter = choose_starter(players=self.players)
        self.players = sort_players(players=self.players, starter=self.starter)
        self.cards.deck = prepare_cards(players=self.players, deck=self.cards.deck)
        for player in self.players:
            print(player.player_cards)
            self.game_choosers = play_game_decision(player=player, renderer=self.renderer, game_choosers=self.game_choosers)
        self.game_mode = players_choose_game(renderer=self.renderer, cards=self.cards, game_choosers=self.game_choosers,
                                             playable_games=self.playable_games, players=self.players)
        self.game_mode.play_game()
        self.cards.reset_deck()