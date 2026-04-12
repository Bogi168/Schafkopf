from Cards import Card


# regular text
def show_player_cards(player_name: str, player_cards: list[Card]):
    player_card_names = [card.card_name for card in player_cards]
    prepared_list = [
        f"{i}: {player_card_name}"
        for i, player_card_name in enumerate(player_card_names, start=1)
    ]
    return f"\n{player_name}: {" | ".join(prepared_list)}"


# text for inputs
error_message: str = "Your answer is not valid!"

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
