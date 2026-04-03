from enum import Enum, IntEnum
import copy


class Color(Enum):
    EICHEL = 1
    GRUEN = 2
    HERZ = 3
    SCHELLEN = 4

    @property
    def name(self):
        names = {
            Color.EICHEL: "Eichel",
            Color.GRUEN: "Grün",
            Color.HERZ: "Herz",
            Color.SCHELLEN: "Schellen"
        }
        return names[self]

class Type(IntEnum):
    SEVEN = 1
    EIGHT = 2
    NINE = 3
    KOENIG = 4
    TEN = 5
    SAU = 6
    UNTER = 7
    OBER = 8

    @property
    def name(self):
        names = {
            Type.SEVEN: "7",
            Type.EIGHT: "8",
            Type.NINE: "9",
            Type.UNTER: "Unter",
            Type.OBER: "Ober",
            Type.KOENIG: "König",
            Type.TEN: "10",
            Type.SAU: "Sau"
        }
        return names[self]

    @property
    def points(self):
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
    def __init__(self, card_color: Color, card_type: Type, card_rank: int):
        self.card_color: Color = card_color
        self.card_type: Type = card_type
        self.card_rank: int = card_rank
        self.card_name: str = f"{self.card_color.name} {self.card_type.name}"

    def __repr__(self):
        return f"({self.card_name})"


class Cards:
    def __init__(self):
        self.full_deck = [Card(card_color = card_color, card_type = card_type, card_rank = card_type.value)
                          for card_type in Type for card_color in Color]
        self.deck = copy.deepcopy(self.full_deck)

    def reset_deck(self) -> None:
        self.deck = copy.deepcopy(self.full_deck)