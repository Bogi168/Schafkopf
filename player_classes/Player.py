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
    prompt_choose_color,
    prompt_ask_player_shoots,
    show_player_cards,
    show_played_card,
    prompt_ask_player_shoots_back,
)
import random

if TYPE_CHECKING:
    from game_classes.Game import Game
    from system.Renderer import Renderer


class Player:
    """An object that represents a player on the game"""

    def __init__(
        self,
        player_name: str,
        renderer: Renderer,
        game_decision_validator: GameDecisionValidator,
    ) -> None:
        """
        :param player_name: The player's name
        :type player_name: str
        :param renderer: An object to render information
        :type renderer: Renderer
        :param game_decision_validator: An object to validate the game decisions made by the player
        :type game_decision_validator: GameDecisionValidator
        """

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
        """Returns the total points of the player"""

        return sum(card.card_type.points for card in self.collected_cards)

    def is_doubles_game_value(self) -> bool:
        """
        Asks the player whether he wants to double the game value or not
        :return: A boolean indicating whether the player wants to double the game value or not
        :rtype: bool
        """

        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_to_double_game_value(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )
        return decision in self.yes_decisions

    def is_chooses_game(self) -> bool:
        """
        Asks the player whether he wants to choose a game or not
        :return: A boolean indicating whether the player wants to choose a game or not
        :rtype: bool
        """

        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_to_choose_game(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )
        return decision in self.yes_decisions

    def choose_sau_color(self) -> str:
        """
        Asks the player for a sau color
        :return: The sau color chosen by the player
        :rtype: str
        """

        valid_color_inputs: dict[str, Color] = (
            self.game_decision_validator.get_available_sau_color_decisions(
                player_cards=self.player_cards
            )
        )

        sau_color_decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_color(
                player_name=self.player_name, valid_colors=valid_color_inputs
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: x in valid_color_inputs.keys(),
        )
        return sau_color_decision

    def get_sau_color(self) -> Color:
        """
        :return: The sau color chosen by the player
        :rtype: Color
        """

        sau_color_decision = self.choose_sau_color()
        sau_color = self.game_decision_validator.sau_color_mapping[sau_color_decision]
        return sau_color

    def choose_trump_color(self) -> str:
        """
        Asks the player for a trump color
        :return: The trump color chosen by the player
        :rtype: str
        """

        valid_color_inputs: dict[str, Color] = (
            self.game_decision_validator.get_valid_solo_trump_colors()
        )

        trump_color_decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_color(
                player_name=self.player_name, valid_colors=valid_color_inputs
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: x in valid_color_inputs.keys(),
        )
        return trump_color_decision

    def get_trump_color(self) -> Color:
        """
        :return: Sau color chosen by the player
        :rtype: Color
        """

        trump_color_decision = self.choose_trump_color()
        trump_color = self.game_decision_validator.solo_trump_color_mapping[
            trump_color_decision
        ]
        return trump_color

    def choose_game_mode(
        self,
        prev_game_mode: type[Game] | None,
        quitting_possible: bool = False,
    ) -> type[Game] | None:
        """
        Returns a valid game decision input made by the player
        :param prev_game_mode: The previously chosen game mode
        :type prev_game_mode: type[Game] | None
        :param quitting_possible: A boolean value that indicates whether quitting the game choosing process is legal
        :type quitting_possible: bool
        :return: A boolean value which indicates whether the player chose a valid game mode or not
        """

        valid_game_mode_decisions = (
            self.game_decision_validator.get_valid_game_mode_decisions(
                prev_game_mode=prev_game_mode, player_cards=self.player_cards
            )
        )
        decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_game(
                player_name=self.player_name,
                quitting_possible=quitting_possible,
                possible_game_mode_decisions=valid_game_mode_decisions,
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in valid_game_mode_decisions.keys()
            or (x in self.quit_decisions and quitting_possible),
        )
        if decision in self.quit_decisions:
            return None
        else:
            return valid_game_mode_decisions[decision]

    def is_shoots(self) -> bool:
        """
        Asks the player whether he wants to shoot or not.
        By shooting, the player doubles the game value and his team turns to the active team.
        :return: A boolean indicating whether the player wants to shoot or not
        :rtype: bool
        """

        self.renderer.render(
            show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )
        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_player_shoots(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )
        return decision in self.yes_decisions

    def is_shoots_back(self) -> bool:
        """
        Asks the player whether he wants to shoot back after someone else shot at him or not.
        By shooting back, the player doubles the game value and his team turns to the active team.
        :return: A boolean indicating whether the player wants to shoot back or not
        :rtype: bool
        """

        self.renderer.render(
            show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )
        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_player_shoots_back(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )
        return decision in self.yes_decisions

    def is_card_decision_valid_number(self, index_decision: str) -> bool:
        """
        Checks, whether the player chose a valid card number for his next card decision
        :param index_decision: The input made by the player
        :type index_decision: str
        :return: A boolean value which indicates whether the player chose a valid card number or not
        :rtype: bool
        """
        return index_decision.isdigit() and 1 <= int(index_decision) <= len(
            self.player_cards
        )

    def card_decision(
        self,
        played_cards: list[Card],
        move_validator: Callable[[Card], bool],
    ) -> None:
        """
        Asks the player to choose make a card decision
        :param played_cards: A list of cards played by the other players
        :type played_cards: list[Card]
        :param move_validator: A function that checks whether the decision by the player is legal
        :type move_validator: Callable[[Card], bool]
        :rtype: None
        """

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

    def is_shoots(self) -> bool:
        return False

    def is_shoots_back(self) -> bool:
        return False
