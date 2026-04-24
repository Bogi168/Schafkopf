from __future__ import annotations
from typing import TYPE_CHECKING
import random
from system.Renderer import Renderer
from card_classes.Cards import Cards
from player_classes.Player import Player, Bot
from game_classes.Game import Game, Sauspiel, Wenz, Solo, Ramsch
from input_validators.GameDecisionValidator import GameDecisionValidator
from card_classes.CardPowerCalculator import SauspielCardPowerCalculator
from system.custom_exceptions import GamemodeIsNotImplementedError
from system.text import (
    error_message,
    prompt_games_amount,
    prompt_player_name,
    prompt_play_again_message,
    show_player_cards,
    words_of_thanks,
)

if TYPE_CHECKING:
    from card_classes.Cards import Card


class Schafkopf:
    def __init__(
        self, renderer: Renderer, base_price: int, call_price: int, alone_price: int
    ) -> None:
        self.players: list[Player] = []
        self.starter: Player | None = None
        self.game_chooser: Player | None = None
        self.game_choosers: list[Player] = []
        self.amount_game_value_doublers = 0

        self.cards = Cards()
        self.renderer = renderer
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price

        self.game_mapping: dict[str, type[Game]] = {
            "1": Sauspiel,
            "2": Wenz,
            "3": Solo,
        }
        self.game_rank_mapping: dict[type[Game], int] = {
            game: rank for rank, game in enumerate(self.game_mapping.values(), start=1)
        }
        self.game_decision_validator: GameDecisionValidator = GameDecisionValidator(
            game_mapping=self.game_mapping, game_rank_mapping=self.game_rank_mapping
        )

    def _create_players(self) -> list[Player]:
        player_name = self.renderer.ask_with_validation(
            prompt=prompt_player_name,
            error_prefix=error_message,
            preprocess=lambda x: x.strip().capitalize(),
            validator=lambda x: x != "",
        )
        players = [
            Player(
                player_name=player_name,
                renderer=self.renderer,
                game_decision_validator=self.game_decision_validator,
            )
        ]
        for i in range(3):
            players.append(
                Bot(
                    bot_name=f"Bot {i + 1}",
                    renderer=self.renderer,
                    game_decision_validator=self.game_decision_validator,
                )
            )
        return players

    @staticmethod
    def choose_starter(players: list[Player]) -> Player:
        starter = random.choice(players)
        return starter

    @staticmethod
    def get_sorted_players(players: list[Player], starter: Player) -> list[Player]:
        starter_index = players.index(starter)
        players = players[starter_index:] + players[:starter_index]
        return players

    @staticmethod
    def shuffle_cards(cards: list[Card]) -> list[Card]:
        random.shuffle(cards)
        return cards

    def deal_cards(self, cards_amount_per_player: int) -> None:
        self.shuffle_cards(cards=self.cards.deck)
        for player in self.players:
            player.player_cards.extend(self.cards.deck[-cards_amount_per_player:])
            del self.cards.deck[-cards_amount_per_player:]

    def prepare_cards(self) -> None:
        for player in self.players:
            player.player_cards.clear()
            player.collected_cards.clear()
        self.cards.reset_deck()
        cards_per_dealing_round = len(self.cards.deck) // 2
        cards_per_player_per_dealing_round = cards_per_dealing_round // len(
            self.players
        )
        self.deal_cards(cards_amount_per_player=cards_per_player_per_dealing_round)
        self.sort_player_hands()
        self.amount_game_value_doublers = 0
        for player in self.players:
            self.renderer.render(
                message=show_player_cards(
                    player_name=player.player_name, player_cards=player.player_cards
                )
            )
            if player.is_doubles_game_value():
                self.amount_game_value_doublers += 1
        self.deal_cards(cards_amount_per_player=cards_per_player_per_dealing_round)
        self.sort_player_hands()

    def prepare_players(self):
        assert self.starter is not None
        self.players = self.get_sorted_players(
            players=self.players, starter=self.starter
        )
        self.game_choosers.clear()

    # sort cards for a Sauspiel -> easier to make game decisions
    def sort_player_hands(self) -> None:
        card_power_calculator = SauspielCardPowerCalculator()
        for player in self.players:
            player.player_cards.sort(
                key=card_power_calculator.get_card_power, reverse=True
            )

    def get_game(self, game_mode: type[Game], player: Player) -> Game:
        assert self.game_chooser is not None
        if game_mode is Sauspiel:
            sau_color = player.get_sau_color()
            return Sauspiel(
                cards=self.cards,
                renderer=self.renderer,
                players=self.players,
                game_chooser=self.game_chooser,
                base_price=self.base_price,
                call_price=self.call_price,
                amount_game_value_doublers=self.amount_game_value_doublers,
                sau_color=sau_color,
            )

        elif game_mode is Wenz:
            return Wenz(
                cards=self.cards,
                renderer=self.renderer,
                players=self.players,
                game_chooser=self.game_chooser,
                base_price=self.base_price,
                alone_price=self.alone_price,
                amount_game_value_doublers=self.amount_game_value_doublers,
            )

        elif game_mode is Solo:
            trump_color = player.get_trump_color()
            return Solo(
                trump_color=trump_color,
                cards=self.cards,
                renderer=self.renderer,
                players=self.players,
                game_chooser=self.game_chooser,
                base_price=self.base_price,
                alone_price=self.alone_price,
                amount_game_value_doublers=self.amount_game_value_doublers,
            )

        else:
            raise GamemodeIsNotImplementedError(f"{game_mode} is not implemented yet")

    def players_choose_game(self) -> Game:
        game_mode: type[Game] | None = None
        game: Game | None = None
        if not self.game_choosers:
            return Ramsch(
                cards=self.cards,
                renderer=self.renderer,
                players=self.players,
                alone_price=self.alone_price,
                amount_game_value_doublers=self.amount_game_value_doublers,
            )
        else:
            for player in self.game_choosers:
                if game_mode is None:
                    decision = player.choose_game_mode(
                        prev_game_mode=game_mode,
                    )
                    game_mode: type[Game] = self.game_mapping[decision]
                    self.game_chooser = player
                    game: Game = self.get_game(game_mode=game_mode, player=player)

                elif game_mode == Solo:
                    assert game is not None
                    return game

                elif (
                    game_mode is not None
                    and self.game_rank_mapping[game_mode]
                    > self.game_rank_mapping[Sauspiel]
                ):
                    decision = player.choose_game_mode(
                        prev_game_mode=game_mode,
                        quitting_possible=True,
                    )
                    if decision == "Q":
                        continue
                    else:
                        game_mode: type[Game] = self.game_mapping[decision]
                        self.game_chooser = player
                        game: Game = self.get_game(game_mode=game_mode, player=player)

                else:
                    decision = player.choose_game_mode(
                        prev_game_mode=game_mode,
                    )
                    game_mode: type[Game] = self.game_mapping[decision]
                    self.game_chooser = player
                    game: Game = self.get_game(game_mode=game_mode, player=player)
        assert game is not None
        return game

    def get_new_starter(self, prev_starter_index: int) -> Player:
        if self.players[prev_starter_index] == self.players[-1]:
            return self.players[0]
        else:
            return self.players[prev_starter_index + 1]

    def main(self) -> None:
        self.players = self._create_players()
        self.starter = self.choose_starter(players=self.players)
        games_amount: str = self.renderer.ask_with_validation(
            prompt=prompt_games_amount,
            error_prefix=error_message,
            validator=lambda x: x.isdigit() and int(x) > 0,
            preprocess=lambda x: x.strip(),
        )
        for game_num in range(int(games_amount)):
            self.prepare_players()
            self.prepare_cards()
            for player in self.players:
                self.renderer.render(
                    message=show_player_cards(
                        player_name=player.player_name, player_cards=player.player_cards
                    )
                )
                if player.is_chooses_game():
                    self.game_choosers.append(player)
            game: Game = self.players_choose_game()
            game.play_game()
            assert self.starter is not None
            self.starter = self.get_new_starter(
                prev_starter_index=self.players.index(self.starter)
            )
            if game_num != int(games_amount) - 1:
                play_again = self.renderer.ask_with_validation(
                    prompt=prompt_play_again_message,
                    error_prefix=error_message,
                    preprocess=lambda x: x.strip().upper(),
                    validator=lambda x: x in ("YES", "Y", "NO", "N"),
                )
                if play_again in ("NO", "N"):
                    break

        self.renderer.render(message=words_of_thanks)
