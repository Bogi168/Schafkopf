import random
from Cards import Color, Card


def shuffle_cards(cards: list):
    random.shuffle(cards)

def order_cards(card: Card, trumps: list):
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

def deal_cards(deck: list, players: list, trumps: list):
    shuffle_cards(cards = deck)
    for player_num in range(len(players)):
        for x in range(8):
            card = deck[-1]
            order_cards(card=card, trumps=trumps)
            players[player_num].player_cards.append(card)
            deck.pop(-1)
        players[player_num].player_cards.sort(key=lambda card: card.card_rank, reverse=True)