import random
from Cards import Color, Card


def shuffle_cards(cards: list) -> list:
    random.shuffle(cards)
    return cards

def adjust_rank(player_cards: list, trumps: list) -> list:
    for card in player_cards:
        if card.card_name in [trump.card_name for trump in trumps]:
            card.card_rank += 100
            match card.card_color:
                case Color.EICHEL:
                    card.card_rank += 0.8
                case Color.GRUEN:
                    card.card_rank += 0.6
                case Color.HERZ:
                    card.card_rank += 0.4
                case Color.SCHELLEN:
                    card.card_rank += 0.2
        elif card.card_name not in [trump.card_name for trump in trumps]:
            match card.card_color:
                case Color.EICHEL:
                    card.card_rank += 80
                case Color.GRUEN:
                    card.card_rank += 60
                case Color.HERZ:
                    card.card_rank += 40
                case Color.SCHELLEN:
                    card.card_rank += 20
    return player_cards

def deal_cards(deck: list, players: list) -> list:
    deck = shuffle_cards(cards = deck)
    for player_num in range(len(players)):
        for x in range(8):
            card = deck[-1]
            players[player_num].player_cards.append(card)
            deck.pop(-1)
        players[player_num].player_cards.sort(key=lambda sort_card: sort_card.card_rank, reverse=True)
    return deck

def prepare_cards(players: list, deck: list) -> list:
    for player in players:
        player.player_cards.clear()
        player.collected_cards.clear()
    deck = deal_cards(deck=deck, players=players)
    return deck

def compare_card_rank(first_card: Card, second_card: Card):
    if first_card.card_rank > second_card.card_rank:
        return first_card
    else:
        return second_card

def find_strongest_card(played_cards: list, trumps: list):
    lead_card = played_cards[0]
    strongest_card = lead_card
    for played_card in played_cards:

        trump_names_list = [trump.card_name for trump in trumps]

        # played_card != Trump -> strongest_card = Trump -> strongest_card = strongest_card
        if played_card.card_name not in trump_names_list and strongest_card.card_name in trump_names_list:
            pass

        # played_card = Trump -> strongest_card != Trump -> strongest_card = played_card
        elif played_card.card_name in trump_names_list and strongest_card.card_name not in trump_names_list:
            strongest_card = played_card

        # played_card = Trump -> strongest_card = Trump -> compare ranks
        elif played_card.card_name in trump_names_list and strongest_card.card_name in trump_names_list:
            strongest_card = compare_card_rank(first_card=strongest_card, second_card=played_card)

        # strongest_card + played_card != Trump -> played_card_color != lead_card_color -> strongest_card = strongest_card
        elif played_card.card_color != lead_card.card_color:
            pass

        # strongest_card + played_card != Trump -> played_card_color = lead_card_color -> compare ranks
        else:
            strongest_card = compare_card_rank(first_card=strongest_card, second_card=played_card)

    return strongest_card