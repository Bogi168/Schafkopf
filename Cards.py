class Card:
    def __init__(self, card_symbol: str, card_type: str, card_value: int):
        self.card_symbol = card_symbol
        self.card_type = card_type
        self.card_name = self.card_symbol + " " + self.card_type
        self.card_value = card_value

    def __repr__(self):
        return f"({self.card_name})"

class Ober(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "Ober", card_value = 3)

class Unter(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "Unter", card_value = 2)

class Sau(Card):
    def __init__(self, card_symbol: str):
        super().__init__(card_symbol = card_symbol, card_type = "Sau", card_value = 11)

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
        self.card_types = (Ober, Unter, Sau, Ten, Koenig, Nine, Eight, Seven)
        self.full_deck = [card_type(card_symbol = card_symbol) for card_type in self.card_types
                          for card_symbol in self.card_symbols]
        self.deck = self.full_deck.copy()

    def reset_deck(self):
        self.deck = self.full_deck.copy()