import random
from Classes.Renderer import Renderer
from Classes.Cards import Cards, Color, Type, Card
from Classes.Player import Player
from Classes.Game import Game, Sauspiel, Wenz, Solo, Ramsch
from functions.handle_game_decision import (
    check_available_game_decisions,
    check_available_sau_color_decisions,
    convert_sau_color_value,
    convert_sau_color_index,
    check_player_quits,
)
from functions.handle_cards import prepare_cards


class Schafkopf:
    def __init__(
        self, renderer: Renderer, base_price: int, call_price: int, alone_price: int
    ) -> None:
        self.playable_games: list[type[Game]] = [Sauspiel, Wenz, Solo]
        self.players: list[Player] = []
        self.starter: Player | None = None
        self.game_choosers: list[Player] = []
        self.game_chooser: Player | None = None
        self.game_mode: Game | None = None

        self.cards = Cards()
        self.renderer = renderer
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price

    def _create_players(self) -> list[Player]:
        player_name = self.renderer.ask_player_name()
        if player_name == "":
            player_name = self.renderer.reask_player_name()
        players = [Player(player_name=player_name)]
        for i in range(3):
            players.append(Player(f"Bot {i + 1}"))
        return players

    def _ask_player_game_decision(self, player: Player) -> None:
        decision = self.renderer.ask_player_game(player_name=player.player_name)
        while decision not in ("YES", "Y", "NO", "N"):
            decision = self.renderer.reask_player_game(player_name=player.player_name)
        if decision in ("YES", "Y"):
            self.game_choosers.append(player)

    @staticmethod
    def choose_starter(players: list[Player]) -> Player:
        starter = random.choice(players)
        return starter

    @staticmethod
    def sort_players(players: list[Player], starter: Player) -> list[Player]:
        found_beginner = False
        while not found_beginner:
            player = players[0]
            if not player == starter:
                players.append(player)
                players.pop(0)
            else:
                found_beginner = True
        return players

    def adjust_rank(self) -> None:
        trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in [Type.OBER, Type.UNTER]
            or card.card_color == Color.HERZ
        ]
        for player in self.players:
            for card in player.player_cards:
                if card.card_name in [trump.card_name for trump in trumps]:
                    card.card_rank += 100
                    match card.card_color:
                        case Color.EICHEL:
                            card.card_rank += 0.8
                        case Color.GRUEN:
                            card.card_rank += 0.6
                        case Color.HERZ:
                            card.card_rank += 0.4
                        case Color.SCHELLEN:
                            card.card_rank += 0.2
                elif card.card_name not in [trump.card_name for trump in trumps]:
                    match card.card_color:
                        case Color.EICHEL:
                            card.card_rank += 80
                        case Color.GRUEN:
                            card.card_rank += 60
                        case Color.HERZ:
                            card.card_rank += 40
                        case Color.SCHELLEN:
                            card.card_rank += 20
                player.player_cards.sort(
                    key=lambda sort_card: sort_card.card_rank, reverse=True
                )

    def reset_rank(self) -> None:
        for player in self.players:
            for card in player.player_cards:
                card.card_rank = card.card_type.value
            player.player_cards.sort(
                key=lambda sort_card: sort_card.card_rank, reverse=True
            )

    def choose_game_decision(
        self, player: Player, prev_game: Game | None, quitting_possible: bool = False
    ) -> str:
        player_name = player.player_name
        player_cards = player.player_cards
        available_decisions = check_available_game_decisions(
            playable_games=self.playable_games,
            prev_game=prev_game,
            player_cards=player_cards,
        )
        decision = self.renderer.player_choose_game(player_name)
        while decision not in available_decisions and not check_player_quits(
            quitting_possible=quitting_possible, decision=decision
        ):
            decision = self.renderer.player_rechoose_game(player_name=player_name)
        if decision == "QUIT":
            decision = "Q"
        if decision != "Q":
            self.game_chooser = player
        match decision:
            case "Q":
                pass
            case "1":
                sau_colors = [Color.EICHEL, Color.GRUEN, Color.SCHELLEN]
                available_colors = check_available_sau_color_decisions(
                    player_cards=player_cards, playable_colors=sau_colors.copy()
                )
                sau_color_decision = self.renderer.player_choose_sau_color()
                sau_color_value = convert_sau_color_value(decision=sau_color_decision)
                sau_color_index = convert_sau_color_index(decision=sau_color_decision)
                while (
                    sau_color_value not in [color.value for color in sau_colors]
                    or sau_colors[sau_color_index] not in available_colors
                ):
                    sau_color_decision = self.renderer.player_rechoose_sau_color()
                    sau_color_value = convert_sau_color_value(
                        decision=sau_color_decision
                    )
                    sau_color_index = convert_sau_color_index(
                        decision=sau_color_decision
                    )
                sau_color = sau_colors[sau_color_index]
                self.game_mode = Sauspiel(
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    call_price=self.call_price,
                    alone_price=self.alone_price,
                    sau_color=sau_color,
                )
            case "2":
                self.game_mode = Wenz(
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    call_price=self.call_price,
                    alone_price=self.alone_price,
                )
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
                self.game_mode = Solo(
                    trump_color=trump_color,
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    call_price=self.call_price,
                    alone_price=self.alone_price,
                )
        return decision

    def players_choose_game(self) -> None:
        if len(self.game_choosers) == 0:
            self.game_mode = Ramsch(
                cards=self.cards,
                renderer=self.renderer,
                players=self.players,
                game_chooser=self.game_chooser,
                base_price=self.base_price,
                call_price=self.call_price,
                alone_price=self.alone_price,
            )
        else:
            for player in self.game_choosers:
                if self.game_mode is None:
                    self.choose_game_decision(player=player, prev_game=self.game_mode)
                elif self.game_mode.rank == 3:
                    pass
                elif self.game_mode.rank > 1:
                    self.choose_game_decision(
                        player=player, prev_game=self.game_mode, quitting_possible=True
                    )
                else:
                    self.choose_game_decision(player=player, prev_game=self.game_mode)

    def main(self) -> None:
        self.players = self._create_players()
        self.starter = self.choose_starter(players=self.players)
        self.players = self.sort_players(players=self.players, starter=self.starter)
        self.cards.deck = prepare_cards(players=self.players, deck=self.cards.deck)
        self.adjust_rank()
        for player in self.players:
            print(player.player_cards)
            self._ask_player_game_decision(player=player)
        self.players_choose_game()
        self.reset_rank()
        self.game_mode.play_game()
        self.cards.reset_deck()
