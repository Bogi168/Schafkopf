from typing import Callable
from Classes.Renderer import Renderer
from Classes.Cards import Card


class Player:
    def __init__(self, player_name: str) -> None:
        self.player_name = player_name
        self.player_cards: list[Card] = []
        self.collected_cards: list[Card] = []
        self.money: int = 0

    def __repr__(self) -> str:
        return self.player_name

    def choose_game_decision(self) -> None:
        pass

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
