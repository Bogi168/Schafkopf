from Player import Player
from Renderer import Renderer
from Cards import Color, Type
from Game import Game

def play_game_decision(player: Player, renderer: Renderer, game_choosers: list):
    decision = renderer.ask_player_game(player_name=player.player_name)
    while decision not in ("YES", "Y", "NO", "N"):
        decision = renderer.reask_player_game(player_name=player.player_name)
    if decision in ("YES", "Y"):
        game_choosers.append(player)
    return game_choosers

def check_player_quits(quitting_possible: bool, decision: str):
    quitting_code_words = ["QUIT", "Q"]
    player_quits = False
    if quitting_possible and decision in quitting_code_words:
        player_quits = True
    return player_quits

def count_color_cards(player_cards: list, color: Color, trump_types: list):
    count = 0
    for card in player_cards:
        if card.card_color == color and card.card_type not in trump_types:
            count += 1
    return count

def check_player_has_sau(sau_color: Color, player_cards: list) -> bool:
    player_has_sau = False
    for card in player_cards:
        if card.card_color == sau_color and card.card_type == Type.SAU:
            player_has_sau = True
    return player_has_sau

def check_sau_color_available(player_cards: list) -> bool:
    colors = (Color.EICHEL, Color.GRUEN, Color.SCHELLEN)
    eichel_count = 0
    gruen_count = 0
    schellen_count = 0

    for card_color in colors:
        match card_color:
            case Color.EICHEL:
                eichel_count = count_color_cards(player_cards=player_cards, color=card_color, trump_types=[Type.OBER, Type.UNTER])
            case Color.GRUEN:
                gruen_count = count_color_cards(player_cards=player_cards, color=card_color, trump_types=[Type.OBER, Type.UNTER])
            case Color.SCHELLEN:
                schellen_count = count_color_cards(player_cards=player_cards, color=card_color, trump_types=[Type.OBER, Type.UNTER])

    for color in colors:
        if check_player_has_sau(color, player_cards=player_cards):
            match color:
                case Color.EICHEL:
                    eichel_count = 0
                case Color.GRUEN:
                    gruen_count = 0
                case Color.SCHELLEN:
                    schellen_count = 0

    return eichel_count + gruen_count + schellen_count != 0

def check_available_game_decisions(playable_games: list, prev_game: Game, player_cards: list) -> list:
    if prev_game is None:
        prev_game_rank = 0
    else:
        prev_game_rank = prev_game.rank

    if prev_game_rank != 0:
        available_game_ranks = [str(game.rank) for game in playable_games if game.rank > prev_game_rank]
    else:
        color_available = check_sau_color_available(player_cards=player_cards)
        if color_available:
            available_game_ranks = [str(game.rank) for game in playable_games]
        else:
            available_game_ranks = [str(game.rank) for game in playable_games if game.rank != 1]
    return available_game_ranks

def check_available_sau_color_decisions(player_cards: list, playable_colors: list) -> list:
    for color in playable_colors.copy():
        player_has_sau = check_player_has_sau(player_cards=player_cards, sau_color=color)
        color_count = count_color_cards(player_cards=player_cards, color=color, trump_types=[Type.OBER, Type.UNTER])
        if color_count == 0 or player_has_sau:
            playable_colors.remove(color)
    return playable_colors

def convert_sau_color_value(decision: str) -> int:
    sau_color_decision = decision
    match decision:
        case "1":
            sau_color_decision = 1
        case "2":
            sau_color_decision = 2
        case "3":
            sau_color_decision = 4
    return sau_color_decision

def convert_sau_color_index(decision: str) -> int:
    sau_color_decision = decision
    match decision:
        case "1":
            sau_color_decision = 0
        case "2":
            sau_color_decision = 1
        case "3":
            sau_color_decision = 2
    return sau_color_decision


if __name__== "__main__":
    pass