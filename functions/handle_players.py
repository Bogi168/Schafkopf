from Clases.Player import Player
import random


def choose_starter(players: list[Player]) -> Player:
    starter = random.choice(players)
    return starter


def sort_players(players: list[Player], starter: Player) -> list[Player]:
    found_beginner = False
    while not found_beginner:
        player = players[0]
        if not player == starter:
            players.append(player)
            players.pop(0)
        else:
            found_beginner = True
    return players
