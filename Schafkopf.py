from Renderer import Renderer
from Cards import Cards
from Game import Sauspiel, Wenz, Solo
from handle_players import create_players, choose_starter, sort_players
from handle_game_decision import play_game_decision, choose_game_decision
from handle_cards import prepare_cards


class Schafkopf:
    def __init__(self, renderer: Renderer):
        self.playable_games = [Sauspiel, Wenz, Solo]
        self.players = []
        self.starter = None
        self.game_choosers = []
        self.game_chooser = None
        self.game_mode = None

        self.cards = Cards()
        self.renderer = renderer

    def players_choose_game(self):
        if len(self.game_choosers) == 0:
            self.game_mode = None
        else:
            for player in self.game_choosers:
                if player == self.game_choosers[0]:
                    self.game_mode = choose_game_decision(renderer=self.renderer, player_name=player.player_name,
                                                     playable_games=self.playable_games,
                                                     cards=self.cards, players=self.players, prev_game_rank=0)
                    self.game_chooser = player
                else:
                    # Fehlt: Wenn Vorgänger spielt Wenz oder Solo -> Abbruch möglich bzw. zwingend
                    self.game_mode = choose_game_decision(renderer=self.renderer, player_name=player.player_name,
                                                     playable_games=self.playable_games,
                                                     cards=self.cards, players=self.players, prev_game_rank=self.game_mode.rank)
                    self.game_chooser = player

    def main(self):
        self.players = create_players(renderer=self.renderer)
        self.starter = choose_starter(players=self.players)
        self.players = sort_players(players=self.players, starter=self.starter)
        self.cards.deck = prepare_cards(players=self.players, deck=self.cards.deck)
        for player in self.players:
            print(player.player_cards)
            self.game_choosers = play_game_decision(player=player, renderer=self.renderer, game_choosers=self.game_choosers)
        self.players_choose_game()
        self.game_mode.play_game(chooser=self.game_chooser)
        self.cards.reset_deck()