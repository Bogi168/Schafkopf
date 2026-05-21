from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from card_classes.Cards import Card, Color
    from player_classes.Player import Player
    from player_classes.Team import Team
    from game_classes.Game import Game
    from money_handling.MoneyDistributer import MoneyDistributer


# regular text
def show_player_cards(player_name: str, player_cards: list[Card]) -> str:
    player_card_names = [card.card_name for card in player_cards]
    prepared_list = [
        f"{i}: {player_card_name}"
        for i, player_card_name in enumerate(player_card_names, start=1)
    ]
    return f"\n{player_name}: {" | ".join(prepared_list)}"


def show_played_card(player_name: str, decision: Card) -> str:
    return f"\n{player_name} played the card: {decision.card_name}"


def show_played_cards(played_cards: list[Card]) -> str:
    played_card_names = [card.card_name for card in played_cards]
    return f"The played cards are: {" | ".join(played_card_names)}"


def show_collector_of_cards(player_name: str, collected_cards: list[Card]) -> str:
    collected_cards_names = [
        collected_card.card_name for collected_card in collected_cards
    ]
    return f"\n{player_name} collected {", ".join(collected_cards_names[-4:])}\n"


def tell_most_point_teams(most_point_teams: list[Team]) -> str:
    most_point_team_names = [team.team_name for team in most_point_teams]
    if len(most_point_teams) == 1:
        return f"The team with the most points is: {most_point_teams[0].team_name}"
    else:
        return f"The teams with the most points are: {", ".join(most_point_team_names)}"


def tell_team_players(team_name: str, players: list[Player]) -> str:
    player_names = [player.player_name for player in players]
    if len(players) == 1:
        return f"The only player in {team_name} is: {player_names[0]}"
    else:
        return f"The players in {team_name} are: {", ".join(player_names)}"


def tell_team_points(team_name: str, points: int) -> str:
    return f"{team_name} has {points} points"


def tell_winners(winners: list[Player]) -> str:
    winner_names = [winner.player_name for winner in winners]
    if len(winners) == 1:
        return f"The only game winner is: {winner_names[0]}"
    else:
        return f"The game winners are: {", ".join(winner_names)}"


def tell_game_value_calculation(
    money_distributer: MoneyDistributer,
    game_value: int,
) -> str:
    from money_handling.MoneyDistributer import (
        SauspielMoneyDistributer,
        RamschMoneyDistributer,
    )

    if isinstance(money_distributer, SauspielMoneyDistributer):
        string = f"\n{"Call price:":<11} {money_distributer.call_price} cents\n"
    else:
        string = f"\n{"Alone price:":<11} {money_distributer.alone_price} cents\n"
    if money_distributer.schneider:
        string += f"{"Schneider:":<11} + {money_distributer.base_price} cents\n"
    if money_distributer.black:
        string += f"{"Black:":<11} + {money_distributer.base_price} cents\n"
    if money_distributer.runners_amount:
        string += f"{"Runners:":<11} + {money_distributer.runners_amount * money_distributer.base_price} cents\n"
    if money_distributer.amount_game_value_doubles:
        string += (
            f"{"Doubles:":<11} * {2 ** money_distributer.amount_game_value_doubles}\n"
        )
    if isinstance(money_distributer, RamschMoneyDistributer):
        virgins_amount: int = money_distributer.count_virgins()
        if virgins_amount:
            string += f"{"Virgins:":<11} * {2 ** virgins_amount}\n"
    string += f"\nThe game value is: {game_value}\n"
    return string


def tell_player_money(player_name: str, money: int) -> str:
    return f"{player_name:<6} has {money:^5} cents"


words_of_thanks = "\nThank you for playing!"

# text for inputs
error_message: str = "Your input is not valid!"

prompt_player_name: str = "\nEnter your name: "
prompt_play_again_message: str = "\nDo you want to play again? (Y/N): "


def prompt_ask_to_double_game_value(player_name: str) -> str:
    return f"{player_name}: Do you want to double the game value? (Y/N): "


def prompt_ask_to_choose_game(player_name: str) -> str:
    return f"{player_name}: Do you want to choose a game (Y/N): "


def prompt_choose_game(
    player_name: str,
    quitting_possible: bool,
    possible_game_mode_decisions: dict[str, type[Game]],
) -> str:
    prepared_game_mode_decisions: list[str] = [
        f"{key}: {game_mode.name}"
        for key, game_mode in possible_game_mode_decisions.items()
    ]
    if quitting_possible:
        return f"\n{player_name}: Which game do you want to choose? ({", ".join(prepared_game_mode_decisions)}) (Q to quit): "
    else:
        return f"\n{player_name}: Which game do you want to choose? ({", ".join(prepared_game_mode_decisions)}): "


def prompt_choose_color(player_name: str, valid_colors: dict[str, Color]) -> str:
    prepared_color_decisions: list[str] = [
        f"{key}: {color.name}" for key, color in valid_colors.items()
    ]
    return f"{player_name}: Which color? ({", ".join(prepared_color_decisions)}): "


def prompt_ask_player_shoots(player_name: str) -> str:
    return f"{player_name}: Do you want to shoot? (Y/N): "


def prompt_ask_player_shoots_back(player_name: str) -> str:
    return f"{player_name}: Do you want to shoot back? (Y/N): "


def prompt_ask_player_card_decision(player_name: str, player_cards: list[Card]) -> str:
    return f"{player_name}: Which card do you want to play? (1-{len(player_cards)}): "
