import random
from Cards import Color, Card


def shuffle_cards(cards: list) -> list:
    random.shuffle(cards)
    return cards

def adjust_rank(card: Card, trumps: list) -> Card:
    if card in trumps:
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
    elif card not in trumps:
        match card.card_color:
            case Color.EICHEL:
                card.card_rank += 80
            case Color.GRUEN:
                card.card_rank += 60
            case Color.HERZ:
                card.card_rank += 40
            case Color.SCHELLEN:
                card.card_rank += 20
    return card

def deal_cards(deck: list, players: list, trumps: list) -> list:
    deck = shuffle_cards(cards = deck)
    for player_num in range(len(players)):
        for x in range(8):
            card = adjust_rank(card=deck[-1], trumps=trumps)
            players[player_num].player_cards.append(card)
            deck.pop(-1)
        players[player_num].player_cards.sort(key=lambda sort_card: sort_card.card_rank, reverse=True)
    return deck