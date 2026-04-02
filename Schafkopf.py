from Renderer import Renderer
from Cards import Cards, Color
from Player import Player
from Game import Sauspiel, Wenz, Solo
from handle_players import create_players, choose_starter, sort_players
from handle_game_decision import play_game_decision, check_available_game_decisions, check_available_sau_color_decisions, convert_sau_color_value, convert_sau_color_index
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

    def choose_game_decision(self, player: Player, prev_game):
        player_name = player.player_name
        player_cards = player.player_cards
        available_decisions = check_available_game_decisions(playable_games = self.playable_games, prev_game=prev_game, player_cards=player_cards)
        decision = self.renderer.player_choose_game(player_name)
        while decision not in available_decisions:
            decision = self.renderer.reask_player_game(player_name=player_name)
        match decision:
            case "1":
                sau_colors = [Color.EICHEL, Color.GRUEN, Color.SCHELLEN]
                available_colors = check_available_sau_color_decisions(player_cards=player_cards,
                                                                       playable_colors=sau_colors.copy())
                sau_color_decision = self.renderer.player_choose_sau_color()
                sau_color_value = convert_sau_color_value(decision=sau_color_decision)
                sau_color_index = convert_sau_color_index(decision=sau_color_decision)
                while (sau_color_value not in [color.value for color in sau_colors]
                       or sau_colors[sau_color_index] not in available_colors):
                    sau_color_decision = self.renderer.player_rechoose_sau_color()
                    sau_color_value = convert_sau_color_value(decision=sau_color_decision)
                    sau_color_index = convert_sau_color_index(decision=sau_color_decision)
                sau_color = sau_colors[sau_color_index]
                self.game_mode = Sauspiel(cards=self.cards, renderer=self.renderer, players=self.players, sau_color=sau_color)
            case "2":
                self.game_mode = Wenz(cards=self.cards, renderer=self.renderer, players=self.players)
            case "3":
                trump_color = self.renderer.player_choose_solo_color()
                while trump_color not in ("1", "2", "3", "4"):
                    trump_color = self.renderer.player_rechoose_solo_color()
                match trump_color:
                    case "1":
                        trump_color = Color.EICHEL
                    case "2":
                        trump_color = Color.GRUEN
                    case "3":
                        trump_color = Color.HERZ
                    case "4":
                        trump_color = Color.SCHELLEN
                self.game_mode = Solo(trump_color=trump_color, cards=self.cards, renderer=self.renderer, players=self.players)

    def players_choose_game(self):
        if len(self.game_choosers) == 0:
            self.game_mode = None
        else:
            for player in self.game_choosers:
                # Fehlt: Wenn Vorgänger spielt Wenz oder Solo -> Abbruch möglich bzw. zwingend
                self.choose_game_decision(player=player, prev_game=self.game_mode)
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