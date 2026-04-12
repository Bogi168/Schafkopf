from typing import Callable
from Renderer import Renderer
from Cards import Card
from text import (
    error_message,
    prompt_ask_player_card_decision,
    show_player_cards,
    show_played_card,
)
import random


class Player:
    def __init__(self, player_name: str) -> None:
        self.player_name = player_name
        self.player_cards: list[Card] = []
        self.collected_cards: list[Card] = []
        self.money: int = 0

    def __repr__(self) -> str:
        return self.player_name

    @property
    def points(self) -> int:
        points = 0
        for card in self.collected_cards:
            points += card.card_type.points
        return points

    def is_decision_valid_number(self, index_decision: str) -> bool:
        return index_decision in ("1", "2", "3", "4", "5", "6", "7", "8") and int(
            index_decision
        ) <= len(self.player_cards)

    def card_decision(
        self,
        renderer: Renderer,
        played_cards: list[Card],
        move_validator: Callable[[Card], bool],
    ) -> None:
        renderer.render(
            message=show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )
        index_decision = renderer.ask_with_validation(
            prompt=prompt_ask_player_card_decision(
                player_name=self.player_name, player_cards=self.player_cards
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: self.is_decision_valid_number(x)
            and move_validator(self.player_cards[int(x) - 1]),
        )
        decision = self.player_cards[int(index_decision) - 1]
        played_cards.append(decision)
        self.player_cards.remove(decision)


class Bot(Player):
    def __init__(self, player_name: str) -> None:
        super().__init__(player_name=player_name)

    def card_decision(
        self,
        renderer: Renderer,
        played_cards: list[Card],
        move_validator: Callable[[Card], bool],
    ) -> None:
        legal_cards = []
        for card in self.player_cards:
            legal = move_validator(card)
            if legal:
                legal_cards.append(card)
        decision = random.choice(legal_cards)
        played_cards.append(decision)
        renderer.render(
            message=show_played_card(player_name=self.player_name, decision=decision)
        )
        self.player_cards.remove(decision)
