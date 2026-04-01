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