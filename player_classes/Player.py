from __future__ import annotations
from typing import Callable, TYPE_CHECKING
from input_validators.GameDecisionValidator import GameDecisionValidator
from card_classes.Cards import Card, Color
from system.text import (
    error_message,
    prompt_ask_player_card_decision,
    prompt_ask_to_double_game_value,
    prompt_ask_to_choose_game,
    prompt_choose_game,
    prompt_choose_sau_color,
    prompt_choose_solo_color,
    show_player_cards,
    show_played_card,
)
import random

if TYPE_CHECKING:
    from game_classes.Game import Game
    from system.Renderer import Renderer


class Player:
    def __init__(
        self,
        player_name: str,
        renderer: Renderer,
        game_decision_validator: GameDecisionValidator,
    ) -> None:
        self.player_name = player_name
        self.renderer = renderer
        self.game_decision_validator: GameDecisionValidator = game_decision_validator
        self.player_cards: list[Card] = []
        self.collected_cards: list[Card] = []
        self.money: int = 0
        self.yes_decisions = ("Y", "YES")
        self.no_decisions = ("N", "NO")
        self.string_decisions = self.yes_decisions + self.no_decisions
        self.quit_decisions = ("QUIT", "Q")

    def __repr__(self) -> str:
        return self.player_name

    @property
    def points(self) -> int:
        return sum(card.card_type.points for card in self.collected_cards)

    def ask_double_game_value(self, amount_game_value_doublers: int) -> int:
        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_to_double_game_value(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )
        if decision in self.yes_decisions:
            amount_game_value_doublers += 1
        return amount_game_value_doublers

    def ask_choose_decision(self, game_choosers: list[Player]) -> list[Player]:
        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_to_choose_game(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )
        if decision in self.yes_decisions:
            game_choosers.append(self)
        return game_choosers

    def choose_sau_color(self) -> str:
        sau_color_decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_sau_color(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: x
            in self.game_decision_validator.get_valid_call_sau_colors(
                player_cards=self.player_cards
            ),
        )
        return sau_color_decision

    def get_sau_color(self) -> Color:
        sau_color_decision = self.choose_sau_color()
        sau_color = self.game_decision_validator.sau_color_mapping[sau_color_decision]
        return sau_color

    def choose_trump_color(self) -> str:
        trump_color_decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_solo_color(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: x
            in self.game_decision_validator.get_valid_solo_trump_colors(),
        )
        return trump_color_decision

    def get_trump_color(self) -> Color:
        trump_color_decision = self.choose_trump_color()
        trump_color = self.game_decision_validator.solo_trump_color_mapping[
            trump_color_decision
        ]
        return trump_color

    def choose_game_mode(
        self,
        prev_game_mode: type[Game] | None,
        quitting_possible: bool = False,
    ) -> str:
        valid_game_mode_decisions = (
            self.game_decision_validator.get_valid_game_mode_decisions(
                prev_game_mode=prev_game_mode, player_cards=self.player_cards
            )
        )
        decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_game(
                player_name=self.player_name, quitting_possible=quitting_possible
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in valid_game_mode_decisions
            or (x in self.quit_decisions and quitting_possible),
        )
        if decision in self.quit_decisions:
            decision = "Q"
        return decision

    def is_card_decision_valid_number(self, index_decision: str) -> bool:
        return index_decision.isdigit() and 1 <= int(index_decision) <= len(
            self.player_cards
        )

    def card_decision(
        self,
        played_cards: list[Card],
        move_validator: Callable[[Card], bool],
    ) -> None:
        self.renderer.render(
            message=show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )
        index_decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_player_card_decision(
                player_name=self.player_name, player_cards=self.player_cards
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: self.is_card_decision_valid_number(x)
            and move_validator(self.player_cards[int(x) - 1]),
        )
        decision = self.player_cards[int(index_decision) - 1]
        played_cards.append(decision)
        self.player_cards.remove(decision)


class Bot(Player):
    def __init__(
        self,
        bot_name: str,
        renderer: Renderer,
        game_decision_validator: GameDecisionValidator,
    ):
        super().__init__(
            player_name=bot_name,
            renderer=renderer,
            game_decision_validator=game_decision_validator,
        )

    def card_decision(
        self,
        played_cards: list[Card],
        move_validator: Callable[[Card], bool],
    ) -> None:
        legal_cards = [card for card in self.player_cards if move_validator(card)]
        decision = random.choice(legal_cards)
        played_cards.append(decision)
        self.renderer.render(
            message=show_played_card(player_name=self.player_name, decision=decision)
        )
        self.player_cards.remove(decision)
