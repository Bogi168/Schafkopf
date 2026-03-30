import random

def shuffle_cards(cards: list):
    random.shuffle(cards)

def deal_cards(cards: list, players: list):
    shuffle_cards(cards = cards)
    for player_num in range(len(players)):
        print(cards)
        for x in range(8):
            players[player_num].player_cards.append(cards[-1])
            cards.pop(-1)