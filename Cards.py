from enum import Enum, IntEnum


class Color(Enum):
    SCHELLEN = 4
    HERZ = 3
    GRUEN = 2
    EICHEL = 1

    @property
    def name(self) -> str:
        names = {
            Color.EICHEL: "Eichel",
            Color.GRUEN: "Grün",
            Color.HERZ: "Herz",
            Color.SCHELLEN: "Schellen",
        }
        return names[self]


class Type(IntEnum):
    SEVEN = 1
    EIGHT = 2
    NINE = 3
    KOENIG = 6
    TEN = 7
    SAU = 8
    UNTER = 9
    OBER = 10

    @property
    def name(self) -> str:
        names = {
            Type.SEVEN: "7",
            Type.EIGHT: "8",
            Type.NINE: "9",
            Type.UNTER: "Unter",
            Type.OBER: "Ober",
            Type.KOENIG: "König",
            Type.TEN: "10",
            Type.SAU: "Sau",
        }
        return names[self]

    @property
    def points(self) -> int:
        points = {
            Type.SEVEN: 0,
            Type.EIGHT: 0,
            Type.NINE: 0,
            Type.UNTER: 2,
            Type.OBER: 3,
            Type.KOENIG: 4,
            Type.TEN: 10,
            Type.SAU: 11,
        }
        return points[self]


class Card:
    def __init__(self, card_color: Color, card_type: Type) -> None:
        self.card_color: Color = card_color
        self.card_type: Type = card_type
        self.card_name: str = f"({self.card_color.name} {self.card_type.name})"

    def __repr__(self) -> str:
        return self.card_name


class Cards:
    def __init__(self) -> None:
        self.full_deck: list[Card] = [
            Card(card_color=card_color, card_type=card_type)
            for card_type in Type
            for card_color in Color
        ]
        self.deck: list[Card] = self.full_deck.copy()

    def reset_deck(self) -> None:
        self.deck = self.full_deck.copy()
