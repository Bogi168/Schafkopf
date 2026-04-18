from Cards import Color, Type, Card


class CardPowerCalculator:
    def __init__(self) -> None:
        self.trump_types: list[Type] = []
        self.trump_color_power: int = 100
        self.eichel_power: int = 80
        self.gruen_power: int = 60
        self.herz_power: int = 40
        self.schellen_power: int = 20

    def get_card_power(self, card: Card) -> int:
        trump_type_power = 1000
        trump_type_power_difference = 100
        power = 0

        match card.card_color:
            case Color.EICHEL:
                power = self.eichel_power + card.card_type.value
            case Color.GRUEN:
                power = self.gruen_power + card.card_type.value
            case Color.HERZ:
                power = self.herz_power + card.card_type.value
            case Color.SCHELLEN:
                power = self.schellen_power + card.card_type.value

        for trump_type in self.trump_types:
            if card.card_type == trump_type:
                power += trump_type_power
                return power
            else:
                trump_type_power -= trump_type_power_difference

        return power

    def get_stronger_card(self, first_card: Card, second_card: Card) -> Card:
        if self.get_card_power(card=first_card) > self.get_card_power(second_card):
            return first_card
        else:
            return second_card

    def get_strongest_played_card(
        self, played_cards: list[Card], trumps: list[Card]
    ) -> Card:
        lead_card = played_cards[0]
        strongest_card = lead_card

        for played_card in played_cards:

            # played_card != Trump -> strongest_card == Trump -> strongest_card = strongest_card
            if played_card not in trumps and strongest_card in trumps:
                continue

            # played_card == Trump -> strongest_card != Trump -> strongest_card = played_card
            elif played_card in trumps and strongest_card not in trumps:
                strongest_card = played_card

            # played_card == Trump -> strongest_card == Trump -> compare ranks
            elif played_card in trumps and strongest_card in trumps:
                strongest_card = self.get_stronger_card(
                    first_card=strongest_card, second_card=played_card
                )

            # strongest_card + played_card != Trump -> played_card_color != lead_card_color -> strongest_card = strongest_card
            elif played_card.card_color != lead_card.card_color:
                continue

            # strongest_card + played_card != Trump -> played_card_color == lead_card_color -> compare ranks
            else:
                strongest_card = self.get_stronger_card(
                    first_card=strongest_card, second_card=played_card
                )

        return strongest_card


class RamschCardPowerCalculator(CardPowerCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.trump_color: Color = Color.HERZ
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]

    def get_card_power(self, card: Card) -> int:
        if (
            card.card_type not in self.trump_types
            and card.card_color == self.trump_color
        ):
            power = self.trump_color_power + card.card_type.value
            return power

        power = super().get_card_power(card=card)
        return power


class SauspielCardPowerCalculator(CardPowerCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.trump_color: Color = Color.HERZ
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]

    def get_card_power(self, card: Card) -> int:
        if (
            card.card_type not in self.trump_types
            and card.card_color == self.trump_color
        ):
            power = self.trump_color_power + card.card_type.value
            return power

        power = super().get_card_power(card=card)
        return power


class WenzCardPowerCalculator(CardPowerCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.trump_types: list[Type] = [Type.UNTER]

    def get_card_power(self, card: Card) -> int:
        power = super().get_card_power(card=card)

        if card.card_type == Type.OBER:
            power -= 5
        return power


class SoloCardPowerCalculator(CardPowerCalculator):
    def __init__(self, trump_color: Color) -> None:
        super().__init__()
        self.trump_color: Color = trump_color
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]

    def get_card_power(self, card: Card) -> int:
        if (
            card.card_type not in self.trump_types
            and card.card_color == self.trump_color
        ):
            power = self.trump_color_power + card.card_type.value
            return power

        power = super().get_card_power(card=card)
        return power
