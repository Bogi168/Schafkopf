from Player import Player
from Renderer import Renderer
from Cards import Cards, Color
from Game import Game, Sauspiel, Wenz, Solo

def play_game_decision(player: Player, renderer: Renderer, game_choosers: list):
    decision = renderer.ask_player_game(player_name=player.player_name)
    while decision not in ("YES", "Y", "NO", "N"):
        decision = renderer.reask_player_game(player_name=player.player_name)
    if decision in ("YES", "Y"):
        game_choosers.append(player)
    return game_choosers

def check_available_game_decisions(playable_games: list, prev_game_rank: int) -> list:
    if prev_game_rank != 0:
        available_game_ranks = [str(game.rank) for game in playable_games if game.rank > prev_game_rank]
        return available_game_ranks
    else:
        available_game_ranks = [str(game.rank) for game in playable_games]
        return available_game_ranks


def choose_game_decision(playable_games: list, renderer: Renderer, player_name: str, cards: Cards, players: list, prev_game_rank: int) -> Game:
    # Fehlt: keine freie Farbe -> Sauspiel gesperrt
    available_decisions = check_available_game_decisions(playable_games=playable_games, prev_game_rank=prev_game_rank)
    decision = renderer.player_choose_game(player_name)
    while decision not in available_decisions:
        decision = renderer.reask_player_game(player_name=player_name)
    match decision:
        case "1":
            sau_color = renderer.player_choose_sau_color()
            while sau_color not in ("1", "2", "3"):
                sau_color = renderer.player_rechoose_sau_color()
            match sau_color:
                case "1":
                    sau_color = Color.EICHEL
                case "2":
                    sau_color = Color.GRUEN
                case "3":
                    sau_color = Color.SCHELLEN
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