from typing import Callable
from Renderer import Renderer
from Cards import Card
import random


class Player:
    def __init__(self, player_name: str) -> None:
        self.player_name = player_name
        self.player_cards: list[Card] = []
        self.collected_cards: list[Card] = []
        self.money: int = 0

    def __repr__(self) -> str:
        return self.player_name

    def bool_valid_card_number(self, index_decision: str) -> bool:
        return index_decision in ("1", "2", "3", "4", "5", "6", "7", "8") and int(
            index_decision
        ) <= len(self.player_cards)

    def card_decision(
        self,
        renderer: Renderer,
        played_cards: list[Card],
        move_validator: Callable[[Card], bool],
    ) -> None:
        print(self.player_cards)
        index_decision = renderer.ask_player_card_decision(
            player_name=self.player_name, player_cards=self.player_cards
        )
        while not self.bool_valid_card_number(index_decision=index_decision):
            index_decision = renderer.reask_player_card_decision(
                player_name=self.player_name, player_cards=self.player_cards
            )
            if self.bool_valid_card_number(index_decision=index_decision):
                break
        decision = self.player_cards[int(index_decision) - 1]
        legal = move_validator(decision)
        while not legal:
            index_decision = renderer.reask_player_card_decision(
                self.player_name, player_cards=self.player_cards
            )
            if not self.bool_valid_card_number(index_decision):
                legal = False
            else:
                decision = self.player_cards[int(index_decision) - 1]
                legal = move_validator(decision)
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
        print(f"{self.player_name} played the card: {decision}")
        self.player_cards.remove(decision)
