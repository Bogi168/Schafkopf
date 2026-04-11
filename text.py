from Cards import Card


# inputs
def ask_player_name() -> str:
    return "Enter your name: "


def reask_player_name() -> str:
    return "The name you entered is not valid! Enter your name: "


def ask_player_game(player_name: str) -> str:
    return f"{player_name}: Do you want to choose a game (Y/N): "


def reask_player_game(player_name: str) -> str:
    return (
        f"{player_name}: Your answer is not valid! Do you want to choose a game (Y/N): "
    )


def player_choose_game(player_name: str) -> str:
    return f"{player_name}: Which game do you want to choose? (1: Sauspiel, 2: Wenz, 3: Solo): "


def player_rechoose_game(player_name: str) -> str:
    return f"{player_name}: Your answer is not valid! Which game do you want to choose? (1: Sauspiel, 2: Wenz, 3: Solo): "


def player_choose_sau_color(player_name: str) -> str:
    return f"{player_name}: Which color? (1: Eichel, 2: Grün, 3: Schellen): "


def player_rechoose_sau_color(player_name: str) -> str:
    return f"{player_name}: Your answer is not valid! Which color? (1: Eichel, 2: Grün, 3: Schellen): "


def player_choose_solo_color(player_name: str) -> str:
    return f"{player_name}: Which color? (1: Eichel, 2: Grün, 3: Herz, 4: Schellen): "


def player_rechoose_solo_color(player_name: str) -> str:
    return f"{player_name}: Your answer is not valid! Which color? (1: Eichel, 2: Grün, 3: Herz, 4: Schellen): "


def ask_player_card_decision(player_name: str, player_cards: list[Card]) -> str:
    return f"{player_name}: Which card do you want to play? (1-{len(player_cards)}): "


def reask_player_card_decision(player_name: str, player_cards: list[Card]) -> str:
    return f"{player_name}: That's not a legal move! Which card do you want to play? (1-{len(player_cards)}): "
