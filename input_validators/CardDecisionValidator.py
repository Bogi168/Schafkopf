from __future__ import annotations
from typing import TYPE_CHECKING

from card_classes.Cards import Type

if TYPE_CHECKING:
    from card_classes.Cards import Color, Card


class CardDecisionValidator:
    """An object that checks whether the card decision by a player is legal or not"""

    def __init__(self) -> None:
        self.trump_types: list[Type] = []

    @staticmethod
    def player_has_lead(decision: Card, player_cards: list[Card]):
        return True

    @staticmethod
    def has_trump_available(player_cards: list[Card], trumps: list[Card]) -> bool:
        return any(card in trumps for card in player_cards)

    def lead_card_is_trump(
        self, decision: Card, player_cards: list[Card], trumps: list[Card]
    ) -> bool:
        trump_available = self.has_trump_available(
            player_cards=player_cards, trumps=trumps
        )
        if trump_available:
            return self.is_decision_in_legal_cards(
                decision=decision, legal_cards=trumps
            )
        else:
            return True

    @staticmethod
    def is_decision_in_legal_cards(decision: Card, legal_cards: list[Card]) -> bool:
        return decision in legal_cards

    def count_similar_color_cards(self, player_cards: list[Card], color: Color) -> int:
        color_count = 0
        for card in player_cards:
            if card.card_color == color and card.card_type not in self.trump_types:
                color_count += 1
        return color_count

    def is_player_has_lead_card_color_available(
        self, lead_card: Card, player_cards: list[Card]
    ) -> bool:
        return (
            self.count_similar_color_cards(
                player_cards=player_cards, color=lead_card.card_color
            )
            != 0
        )

    def player_has_lead_card_color_available(
        self, decision: Card, player_cards: list[Card], lead_card: Card
    ) -> bool:
        legal_cards = [
            similar_color_card
            for similar_color_card in player_cards
            if similar_color_card.card_color == lead_card.card_color
            and similar_color_card.card_type not in self.trump_types
        ]
        return self.is_decision_in_legal_cards(
            decision=decision, legal_cards=legal_cards
        )

    @staticmethod
    def player_has_not_lead_card_color_available() -> bool:
        return True

    def lead_card_is_not_trump(
        self, decision: Card, lead_card: Card, player_cards: list[Card]
    ) -> bool:
        similar_color_available = self.is_player_has_lead_card_color_available(
            lead_card=lead_card, player_cards=player_cards
        )
        if similar_color_available:
            return self.player_has_lead_card_color_available(
                decision=decision, lead_card=lead_card, player_cards=player_cards
            )
        else:
            return self.player_has_not_lead_card_color_available()

    def player_has_not_lead(
        self,
        lead_card: Card,
        decision: Card,
        player_cards: list[Card],
        trumps: list[Card],
    ) -> bool:
        if lead_card in trumps:
            return self.lead_card_is_trump(
                decision=decision, player_cards=player_cards, trumps=trumps
            )
        else:
            return self.lead_card_is_not_trump(
                decision=decision, lead_card=lead_card, player_cards=player_cards
            )

    def is_move_legal(
        self,
        decision: Card,
        lead_card: Card | None,
        player_cards: list[Card],
        trumps: list[Card],
    ) -> bool:
        """
        Checks whether the card decision by a player is legal or not
        :param decision: The card decision by the player
        :type decision: Card
        :param lead_card: The first card that was played in the round
        :type lead_card: Card
        :param player_cards: The player's cards
        :type player_cards: list[Card]
        :param trumps: A list of the trump cards
        :type trumps: list[Card]
        """

        if len(player_cards) == 1:
            return True

        if lead_card is None:
            return self.player_has_lead(decision=decision, player_cards=player_cards)

        return self.player_has_not_lead(
            lead_card=lead_card,
            decision=decision,
            player_cards=player_cards,
            trumps=trumps,
        )


class RamschCardDecisionValidator(CardDecisionValidator):
    def __init__(self) -> None:
        super().__init__()
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]


class SauspielCardDecisionValidator(CardDecisionValidator):
    def __init__(self, call_sau: Card) -> None:
        super().__init__()
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]
        self.call_sau: Card = call_sau

    def is_player_owns_call_sau(self, player_cards: list[Card]) -> bool:
        return any(card == self.call_sau for card in player_cards)

    def is_player_allowed_to_run_away(self, player_cards: list[Card]) -> bool:
        return (
            self.is_player_owns_call_sau(player_cards=player_cards)
            and self.count_similar_color_cards(
                player_cards=player_cards, color=self.call_sau.card_color
            )
            >= 4
        )

    def is_plays_call_sau_color(self, decision: Card):
        return (
            decision.card_color == self.call_sau.card_color
            and decision.card_type not in self.trump_types
            and decision != self.call_sau
        )

    def run_away_prohibition(self, decision: Card, player_cards: list[Card]):
        return not self.is_player_allowed_to_run_away(
            player_cards=player_cards
        ) and self.is_plays_call_sau_color(decision=decision)

    def player_has_lead(self, decision: Card, player_cards: list[Card]) -> bool:
        if self.run_away_prohibition(decision=decision, player_cards=player_cards):
            return False
        else:
            return True

    def player_has_lead_card_color_available(
        self, decision: Card, player_cards: list[Card], lead_card: Card
    ) -> bool:
        if (
            self.is_player_owns_call_sau(player_cards=player_cards)
            and lead_card.card_color == self.call_sau.card_color
        ):
            legal_cards = [self.call_sau]
            return self.is_decision_in_legal_cards(
                decision=decision, legal_cards=legal_cards
            )
        else:
            return super().player_has_lead_card_color_available(
                decision=decision, lead_card=lead_card, player_cards=player_cards
            )

    def player_has_not_lead(
        self,
        lead_card: Card,
        decision: Card,
        player_cards: list[Card],
        trumps: list[Card],
    ) -> bool:
        if (
            self.is_player_owns_call_sau(player_cards=player_cards)
            and lead_card.card_color != self.call_sau.card_color
            and decision == self.call_sau
        ):
            return False
        else:
            return super().player_has_not_lead(
                lead_card=lead_card,
                decision=decision,
                player_cards=player_cards,
                trumps=trumps,
            )


class WenzCardDecisionValidator(CardDecisionValidator):
    def __init__(self) -> None:
        super().__init__()
        self.trump_types: list[Type] = [Type.UNTER]


class SoloCardDecisionValidator(CardDecisionValidator):
    def __init__(self) -> None:
        super().__init__()
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]
