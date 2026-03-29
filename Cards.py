class Card:
    def __init__(self, card_symbol: str, card_type: str, card_value: int):
        self.card_symbol = card_symbol
        self.card_type = card_type
        self.card_name = "(" + self.card_symbol + " " + self.card_type + ")"
        self.card_value = card_value

    def __repr__(self):
        return self.card_name

class Ober(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "Ober", card_value = 3)

class Unter(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "Unter", card_value = 2)

class Ass(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "Ass", card_value = 11)

class Koenig(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "König", card_value = 4)

class Ten(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "10", card_value = 10)

class Nine(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "9", card_value = 0)

class Eight(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "8", card_value = 0)

class Seven(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "7", card_value = 0)


class Cards:
    def __init__(self):
        self.card_symbols = ("Eichel", "Grün", "Herz", "Schellen")
        self.card_types = (Ober, Unter, Ass, Ten, Koenig, Nine, Eight, Seven)
        self.full_deck = []

    def create_full_deck(self):
        self.full_deck.clear()
        for card_symbol in self.card_symbols:
            full_deck = [card_type(card_symbol = card_symbol) for card_type in self.card_types]
