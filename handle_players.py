from Player import Player
from Renderer import Renderer
import random


def create_players(renderer: Renderer):
    players = []
    player_name = renderer.ask_player_name()
    if player_name == "":
        player_name = renderer.reask_player_name()
    players.append(Player(player_name=player_name))
    for x in range(3):
        players.append(Player(f"Bot {x+1}"))
    return players


def choose_starter(players: list) -> Player:
    starter = random.choice(players)
    return starter


def sort_players(players: list, starter: Player) -> list:
    found_beginner = False
    while not found_beginner:
        player = players.__getitem__(0)
        if not player == starter:
            players.append(player)
            players.pop(0)
        else:
            found_beginner = True
    return players
