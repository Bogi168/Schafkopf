from Cards import Card
from Game import Game, Sauspiel


def check_lead_card(lead_card: Card) -> bool:
    return lead_card is None

def check_player_owns_call_sau(player_cards: list, call_sau: Card) -> bool:
    player_owns_call_sau = False
    for card in player_cards:
        if card == call_sau:
            player_owns_call_sau = True
    return player_owns_call_sau

def check_lead_card_trump(lead_card: Card, trumps: list) -> bool:
    return lead_card.card_name in [trump.card_name for trump in trumps]

def similar_color_available(lead_card: Card, player_cards: list, trumps: list) -> bool:
    bool_color_available = False
    if not check_lead_card(lead_card=lead_card):
        for card in player_cards:
            if lead_card.card_color == card.card_color and card.card_name not in [trump.card_name for trump in trumps]:
                bool_color_available = True
    return bool_color_available

def trump_available(trumps: list, player_cards: list) -> bool:
    bool_trumps = False
    for card in player_cards:
        if card.card_name in [trump.card_name for trump in trumps]:
            bool_trumps = True
    return bool_trumps

def decision_legal(decision: Card, legal_cards: list) -> bool:
    return decision.card_name in [legal_card.card_name for legal_card in legal_cards]

def is_move_legal(game_mode: Game, decision: Card, player_cards: list, lead_card: Card, trumps: list, call_sau: Card) -> bool:
    lead = check_lead_card(lead_card=lead_card)
    if lead:
        # Fehlt: Davonlaufen
        legal = True
        print("Lead-")
        if (game_mode.__class__ == Sauspiel and check_player_owns_call_sau(player_cards=player_cards, call_sau=call_sau)
                and decision.card_color == call_sau.card_color and decision != call_sau):
                legal = False
    # Player is only allowed to play the call_sau if it is called by the lead_card or the last card he has
    elif (not lead and game_mode.__class__ == Sauspiel
          and check_player_owns_call_sau(player_cards=player_cards, call_sau=call_sau)
          and lead_card.card_color != call_sau.card_color and decision == call_sau):
        if len(player_cards) == 1:
            legal = True
        else:
            legal = False
    else:
        bool_lead_trump = check_lead_card_trump(lead_card=lead_card, trumps=trumps)
        if bool_lead_trump:
            trump_avail = trump_available(trumps=trumps, player_cards=player_cards)
            if trump_avail:
                print("NoLead-LeadTrump-TrumpAvail-")
                legal = decision_legal(decision=decision, legal_cards=trumps)
            else:
                print("NoLead-LeadTrump-NoTrumpAvail-")
                legal = True
        else:
            sim_col_avail = similar_color_available(lead_card=lead_card, player_cards=player_cards, trumps=trumps)
            if sim_col_avail:
                legal_cards = [sim_color for sim_color in player_cards if sim_color.card_color == lead_card.card_color
                               and sim_color.card_name not in [trump.card_name for trump in trumps]]
                if (game_mode.__class__ == Sauspiel and check_player_owns_call_sau(player_cards=player_cards, call_sau=call_sau)
                        and lead_card.card_color == call_sau.card_color):
                    legal_cards = [call_sau]
                print("NoLead-NoLeadTrump-SimColAvail-")
                legal = decision_legal(decision=decision, legal_cards=legal_cards)
            else:
                print("NoLead-NoLeadTrump-NoSimColAvail-")
                legal = True
    print(f"The Move is {legal}")
    return legal