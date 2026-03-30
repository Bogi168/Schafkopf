from Cards import Card

def check_lead_card(played_cards: list) -> bool:
    return len(played_cards) == 0

def check_lead_card_trump(lead_card: Card, trumps: list) -> bool:
    return lead_card in trumps

def similar_color_available(lead_card: Card, player_cards: list) -> bool:
    bool_color_available = False
    if not check_lead_card(played_cards=player_cards):
        for card in player_cards:
            if lead_card.card_color == card.card_color:
                bool_color_available = True
    return bool_color_available

def trump_available(trumps: list, player_cards: list):
    bool_trumps = False
    for card in player_cards:
        if card in trumps:
            bool_trumps = True
    return bool_trumps

def decision_legal(decision: Card, legal_cards: list) -> bool:
    return decision in legal_cards

def is_move_legal(decision: Card, played_cards: list, player_cards: list, lead_card: Card, trumps: list) -> bool:
    lead = check_lead_card(played_cards)
    if lead:
        # Farbe der Rufsau führt zu legal = False
        legal = True
    else:
        lead_trump = check_lead_card_trump(lead_card=lead_card, trumps=trumps)
        if lead_trump:
            trump_avail = trump_available(trumps=trumps, player_cards=player_cards)
            if trump_avail:
                legal = decision_legal(decision=decision, legal_cards=trumps)
            else:
                legal = True
        else:
            sim_col_avail = similar_color_available(lead_card=lead_card, player_cards=player_cards)
            if sim_col_avail:
                legal_cards = [sim_color for sim_color in player_cards if sim_color.card_color == lead_card.card_color]
                legal = decision_legal(decision=decision, legal_cards=legal_cards)
            else:
                legal = True
    return legal
