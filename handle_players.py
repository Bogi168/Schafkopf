from Player import Player
from Renderer import Renderer
from Cards import Cards, Color
from Game import Game, Sauspiel, Wenz, Solo
import random

def create_players(renderer: Renderer):
    players = []
    player_name = renderer.ask_player_name()
    if player_name == "":
        player_name = renderer.reask_player_name()
    players.append(Player(player_name = player_name))
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

def play_game_decision(player: Player, renderer: Renderer, game_choosers: list):
    decision = renderer.ask_player_game(player_name=player.player_name)
    while decision not in ("YES", "Y", "NO", "N"):
        decision = renderer.reask_player_game(player_name=player.player_name)
    if decision in ("YES", "Y"):
        game_choosers.append(player)
    return game_choosers

def choose_game_decision(renderer: Renderer, player_name: str, cards: Cards, players: list) -> Game:
    decision = renderer.player_choose_game(player_name)
    while decision not in ("1", "2", "3"):
        decision = renderer.reask_player_game(player_name=player_name)
    match decision:
        case "1":
            game_mode = Sauspiel(cards=cards, renderer=renderer, players=players)
        case "2":
            game_mode = Wenz(cards=cards, renderer=renderer, players=players)
        case "3":
            trump_color = renderer.player_choose_color()
            while trump_color not in ("1", "2", "3", "4"):
                trump_color = renderer.player_rechoose_color()
            match trump_color:
                case "1":
                    trump_color = Color.EICHEL
                case "2":
                    trump_color = Color.GRUEN
                case "3":
                    trump_color = Color.HERZ
                case "4":
                    trump_color = Color.SCHELLEN
            game_mode = Solo(trump_color=trump_color, cards=cards, renderer=renderer, players=players)
    return game_mode