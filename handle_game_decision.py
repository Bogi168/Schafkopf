from Player import Player
from Renderer import Renderer
from Cards import Cards, Color, Type
from Game import Game, Sauspiel, Wenz, Solo

def play_game_decision(player: Player, renderer: Renderer, game_choosers: list):
    decision = renderer.ask_player_game(player_name=player.player_name)
    while decision not in ("YES", "Y", "NO", "N"):
        decision = renderer.reask_player_game(player_name=player.player_name)
    if decision in ("YES", "Y"):
        game_choosers.append(player)
    return game_choosers

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

def choose_game_decision(playable_games: list, renderer: Renderer, player: Player, cards: Cards, players: list, prev_game) -> Game:
    player_name = player.player_name
    player_cards = player.player_cards
    available_decisions = check_available_game_decisions(playable_games=playable_games, prev_game=prev_game, player_cards=player_cards)
    decision = renderer.player_choose_game(player_name)
    while decision not in available_decisions:
        decision = renderer.reask_player_game(player_name=player_name)
    match decision:
        case "1":
            sau_colors = [Color.EICHEL, Color.GRUEN, Color.SCHELLEN]
            available_colors = check_available_sau_color_decisions(player_cards=player_cards, playable_colors=sau_colors.copy())
            sau_color_decision = renderer.player_choose_sau_color()
            sau_color_value = convert_sau_color_value(decision=sau_color_decision)
            sau_color_index = convert_sau_color_index(decision=sau_color_decision)
            while (sau_color_value not in [color.value for color in sau_colors]
                   or sau_colors[sau_color_index] not in available_colors):
                sau_color_decision = renderer.player_rechoose_sau_color()
                sau_color_value = convert_sau_color_value(decision=sau_color_decision)
                sau_color_index = convert_sau_color_index(decision=sau_color_decision)
            sau_color = sau_colors[sau_color_index]
            game_mode = Sauspiel(cards=cards, renderer=renderer, players=players, sau_color=sau_color)
        case "2":
            game_mode = Wenz(cards=cards, renderer=renderer, players=players)
        case "3":
            trump_color = renderer.player_choose_solo_color()
            while trump_color not in ("1", "2", "3", "4"):
                trump_color = renderer.player_rechoose_solo_color()
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

if __name__== "__main__":
    pass