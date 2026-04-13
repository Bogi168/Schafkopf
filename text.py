from Cards import Card
from Team import Team
from Player import Player


# regular text
def show_player_cards(player_name: str, player_cards: list[Card]):
    player_card_names = [card.card_name for card in player_cards]
    prepared_list = [
        f"{i}: {player_card_name}"
        for i, player_card_name in enumerate(player_card_names, start=1)
    ]
    return f"\n{player_name}: {" | ".join(prepared_list)}"


def show_played_card(player_name: str, decision: Card):
    return f"\n{player_name} played the card: {decision}"


def show_played_cards(played_cards: list[Card]):
    played_card_names = [card.card_name for card in played_cards]
    return f"The played cards are: {" | ".join(played_card_names)}"


def show_collector_of_cards(player_name: str, collected_cards: list[Card]):
    return f"\n{player_name} collected {collected_cards[-4:]}\n"


def tell_most_point_teams(most_point_teams: list[Team]):
    most_point_team_names = [team.team_name for team in most_point_teams]
    if len(most_point_teams) == 1:
        return f"The most point team is: {most_point_teams[0].team_name}"
    else:
        return f"The most point teams are: {", ".join(most_point_team_names)}"


def tell_team_players(team_name: str, players: list[Player]):
    player_names = [player.player_name for player in players]
    if len(players) == 1:
        return f"The only player in {team_name} is {player_names[0]}"
    else:
        return f"The players in {team_name} are {", ".join(player_names)}"


def tell_team_points(team_name: str, points: int):
    return f"{team_name} has {points} points"


def tell_winners(winners: list[Player]):
    winner_names = [winner.player_name for winner in winners]
    if len(winners) == 1:
        return f"The only game winner is {winner_names[0]}"
    else:
        return f"The game winners are {", ".join(winner_names)}"


def tell_player_money(player_name: str, money: int):
    return f"{player_name} has {money} cents"


# text for inputs
error_message: str = "Your input is not valid!"

prompt_player_name: str = "\nEnter your name: "
prompt_games_amount: str = "Enter the amount of games: "


def prompt_ask_to_choose_game(player_name: str) -> str:
    return f"{player_name}: Do you want to choose a game (Y/N): "


def prompt_choose_game(player_name: str, quitting_possible: bool) -> str:
    if quitting_possible:
        return f"{player_name}: Which game do you want to choose? (1: Sauspiel, 2: Wenz, 3: Solo) (Q to quit): "
    else:
        return f"{player_name}: Which game do you want to choose? (1: Sauspiel, 2: Wenz, 3: Solo): "


def prompt_choose_sau_color(player_name: str) -> str:
    return f"{player_name}: Which color? (1: Eichel, 2: Grün, 3: Schellen): "


def prompt_choose_solo_color(player_name: str) -> str:
    return f"{player_name}: Which color? (1: Eichel, 2: Grün, 3: Herz, 4: Schellen): "


def prompt_ask_player_card_decision(player_name: str, player_cards: list[Card]) -> str:
    return f"{player_name}: Which card do you want to play? (1-{len(player_cards)}): "
