from Cards import Card

def similar_color_available(first_card: Card, player_cards: list):
    bool_color_available = False
    if first_card is not None:
        for card in player_cards:
            if first_card.card_color == card.card_color:
                bool_color_available = True
    return bool_color_available

def trump_available(trumps: list, player_cards: list):
    bool_trumps = False
    for card in player_cards:
        if card in trumps:
            bool_trumps = True
    return bool_trumps

