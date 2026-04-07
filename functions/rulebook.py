from Clases.Cards import Card


def check_lead_card(lead_card: Card | None) -> bool:
    return lead_card is None


def check_player_owns_call_sau(player_cards: list[Card], call_sau: Card) -> bool:
    for card in player_cards:
        if card == call_sau:
            return True
    return False


def check_lead_card_trump(lead_card: Card, trumps: list[Card]) -> bool:
    return lead_card.card_name in [trump.card_name for trump in trumps]


def similar_color_available(
    lead_card: Card, player_cards: list[Card], trumps: list[Card]
) -> bool:
    if check_lead_card(lead_card=lead_card):
        return False
    for card in player_cards:
        if lead_card.card_color == card.card_color and card.card_name not in [
            trump.card_name for trump in trumps
        ]:
            return True
    return False


def trump_available(trumps: list[Card], player_cards: list[Card]) -> bool:
    for card in player_cards:
        if card.card_name in [trump.card_name for trump in trumps]:
            return True
    return False


def decision_legal(decision: Card, legal_cards: list[Card]) -> bool:
    return decision.card_name in [legal_card.card_name for legal_card in legal_cards]
