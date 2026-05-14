from __future__ import annotations
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from money_handling.MoneyDistributer import (
    MoneyDistributer,
    RamschMoneyDistributer,
    SauspielMoneyDistributer,
    WenzMoneyDistributer,
    SoloMoneyDistributer,
)

if TYPE_CHECKING:
    from player_classes.Player import Player
    from player_classes.Team import Team

TOTAL_POINTS = 120


def make_distributer(
    cls: type[MoneyDistributer],
    players: list[Player],
    teams: list[Team],
    winners: list[Player],
    active_team: Team | None = None,
    amount_game_value_doubles: int = 0,
    runners_amount: int = 0,
    base_price: int = 10,
    call_price: int = 20,
    alone_price: int = 50,
    amount_game_card_points: int = TOTAL_POINTS,
) -> MoneyDistributer:
    kwargs = dict(
        players=players,
        teams=teams,
        winners=winners,
        amount_game_value_doubles=amount_game_value_doubles,
        amount_game_card_points=amount_game_card_points,
    )
    if cls is RamschMoneyDistributer:
        kwargs["alone_price"] = alone_price
    elif cls is SauspielMoneyDistributer:
        kwargs.update(
            base_price=base_price,
            call_price=call_price,
            active_team=active_team,  # type: ignore
            runners_amount=runners_amount,
        )
    else:  # Wenz / Solo
        kwargs.update(
            base_price=base_price,
            alone_price=alone_price,
            active_team=active_team,  # type: ignore
            runners_amount=runners_amount,
        )
    return cls(**kwargs)


# distribute money


def test_distribute_money_one_winner(
    team_alone_player_1,
    team_three_players_2_3_4,
):
    player_1 = team_alone_player_1.players[0]
    player_2 = team_three_players_2_3_4.players[0]
    player_3 = team_three_players_2_3_4.players[1]
    player_4 = team_three_players_2_3_4.players[2]
    players = [player_1, player_2, player_3, player_4]
    winners: list[Player] = [player_1]

    distributer: MoneyDistributer = make_distributer(
        SoloMoneyDistributer,
        players=players,
        teams=[team_alone_player_1, team_three_players_2_3_4],
        winners=winners,
        active_team=team_alone_player_1,
    )
    game_value: int = 10
    distributer.distribute_money(game_value=game_value, winners=winners)

    assert player_1.money == 3 * game_value
    assert player_2.money == -game_value
    assert player_3.money == -game_value
    assert player_4.money == -game_value


def test_distribute_money_two_winners(
    team_two_players_1,
    team_two_players_2,
):
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]
    winners: list[Player] = [player_1, player_2]

    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=winners,
        active_team=team_two_players_1,
    )
    game_value: int = 10
    distributer.distribute_money(game_value=game_value, winners=winners)

    assert player_1.money == game_value
    assert player_2.money == game_value
    assert player_3.money == -game_value
    assert player_4.money == -game_value


def test_distribute_money_three_winners(
    team_alone_player_1,
    team_three_players_2_3_4,
):
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_three_players_2_3_4.players[0]
    player_3: Player = team_three_players_2_3_4.players[1]
    player_4: Player = team_three_players_2_3_4.players[2]
    players: list[Player] = [player_1, player_2, player_3, player_4]
    winners: list[Player] = [player_2, player_3, player_4]

    distributer: MoneyDistributer = make_distributer(
        WenzMoneyDistributer,
        players=players,
        teams=[team_alone_player_1, team_three_players_2_3_4],
        winners=winners,
        active_team=team_three_players_2_3_4,
    )
    game_value: int = 10
    distributer.distribute_money(game_value=game_value, winners=winners)

    assert player_1.money == -3 * game_value
    assert player_2.money == game_value
    assert player_3.money == game_value
    assert player_4.money == game_value


# basic game value adds


def test_basic_game_value_adds_no_extras(
    team_two_players_1,
    team_two_players_2,
):
    # No runners, no schneider, no black, no doubles → value unchanged
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = 61
    team_two_players_2.points = 59
    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_1,
    )
    assert distributer.basic_game_value_adds(game_value=20) == 20


def test_basic_game_value_adds_runners(
    team_two_players_1,
    team_two_players_2,
):
    # 3 runners with base_price=10 add 30
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = 61
    team_two_players_2.points = 59
    distributer: MoneyDistributer = make_distributer(
        SoloMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        runners_amount=3,
    )
    assert distributer.basic_game_value_adds(game_value=20) == 50


def test_basic_game_value_adds_schneider(
    team_two_players_1,
    team_two_players_2,
):
    # Winning team above schneider threshold (>90) -> adds base_price
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = 91
    team_two_players_2.points = 29
    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_1,
    )
    assert distributer.basic_game_value_adds(game_value=20) == 30


def test_basic_game_value_adds_schneider_threshold_active_team_loses(
    team_two_players_1,
    team_two_players_2,
):
    # Winning team == schneider threshold (90) and active_team != winning_team -> schneider bonus applies
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = 90
    team_two_players_2.points = 30
    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_2,  # active_team is the loser
    )
    assert distributer.basic_game_value_adds(game_value=20) == 30


def test_basic_game_value_adds_schneider_threshold_active_team_wins(
    team_two_players_1,
    team_two_players_2,
):
    # Winning team == schneider threshold (90) and active_team == winning_team -> no schneider bonus.
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = 90
    team_two_players_2.points = 30
    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_1,  # active_team is the winner
    )
    assert distributer.basic_game_value_adds(game_value=20) == 20


def test_basic_game_value_adds_black(
    team_two_players_1,
    team_two_players_2,
):
    # Winning team collects all 120 points → schneider + black bonus
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = TOTAL_POINTS
    team_two_players_2.points = 0
    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_1,
    )
    # 20 (base) + 10 (schneider) + 10 (black) = 40
    assert distributer.basic_game_value_adds(game_value=20) == 40


def test_basic_game_value_adds_doubles(
    team_two_players_1,
    team_two_players_2,
):
    # 2 doubles → value multiplied by 4
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = 61
    team_two_players_2.points = 59
    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        amount_game_value_doubles=2,
    )
    assert distributer.basic_game_value_adds(game_value=20) == 80


# calculate game value


def test_sauspiel_calculate_game_value_base(
    team_two_players_1,
    team_two_players_2,
):
    # Minimal Sauspiel: call_price only
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = 61
    team_two_players_2.points = 59
    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        call_price=20,
    )
    assert distributer.calculate_game_value() == 20


def test_sauspiel_calculate_game_value_with_runners_and_schneider(
    team_two_players_1,
    team_two_players_2,
):
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_two_players_1.points = 91
    team_two_players_2.points = 29
    distributer: MoneyDistributer = make_distributer(
        SauspielMoneyDistributer,
        players=players,
        teams=[team_two_players_1, team_two_players_2],
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        call_price=20,
        runners_amount=3,
    )
    # 20 (call) + 30 (3 runners) + 10 (schneider) = 60
    assert distributer.calculate_game_value() == 60


def test_wenz_calculate_game_value_base(
    team_alone_player_1,
    team_three_players_2_3_4,
):
    # Minimal Wenz: alone_price only
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_three_players_2_3_4.players[0]
    player_3: Player = team_three_players_2_3_4.players[1]
    player_4: Player = team_three_players_2_3_4.players[2]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_alone_player_1.points = 61
    team_three_players_2_3_4.points = 59
    distributer: MoneyDistributer = make_distributer(
        WenzMoneyDistributer,
        players=players,
        teams=[team_alone_player_1, team_three_players_2_3_4],
        winners=[player_1],
        active_team=team_alone_player_1,
        alone_price=50,
    )
    assert distributer.calculate_game_value() == 50


def test_solo_calculate_game_value_with_doubles(
    team_alone_player_1,
    team_three_players_2_3_4,
):
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_three_players_2_3_4.players[0]
    player_3: Player = team_three_players_2_3_4.players[1]
    player_4: Player = team_three_players_2_3_4.players[2]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    team_alone_player_1.points = 61
    team_three_players_2_3_4.points = 59
    distributer: MoneyDistributer = make_distributer(
        SoloMoneyDistributer,
        players=players,
        teams=[team_alone_player_1, team_three_players_2_3_4],
        winners=[player_1],
        active_team=team_alone_player_1,
        alone_price=50,
        amount_game_value_doubles=1,
    )
    assert distributer.calculate_game_value() == 100


def test_ramsch_calculate_game_value_base(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    teams: list[Team] = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    # All the players collected cards -> no virgins
    player_2.collected_cards = [MagicMock()]
    player_1.collected_cards = [MagicMock()]
    player_3.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]

    distributer: MoneyDistributer = make_distributer(
        RamschMoneyDistributer,
        players=players,
        teams=teams,
        winners=[player_2, player_3, player_4],
        alone_price=20,
    )
    assert distributer.calculate_game_value() == 20


def test_ramsch_calculate_game_value_one_virgin(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    # 1 player collected no cards → 1 extra double → alone_price * 2
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    player_2.collected_cards = []
    player_1.collected_cards = [MagicMock()]
    player_3.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]
    teams = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    distributer: MoneyDistributer = make_distributer(
        RamschMoneyDistributer,
        players=players,
        teams=teams,
        winners=[player_1, player_3, player_4],
        alone_price=20,
    )
    assert distributer.calculate_game_value() == 40


def test_ramsch_calculate_game_value_two_virgins(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    # 2 virgins → 2 extra doubles → alone_price * 4
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    player_2.collected_cards = []
    player_3.collected_cards = []
    player_1.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]
    teams: list[Team] = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    distributer: MoneyDistributer = make_distributer(
        RamschMoneyDistributer,
        players=players,
        teams=teams,
        winners=[player_1, player_4],
        alone_price=20,
    )
    assert distributer.calculate_game_value() == 80


def test_ramsch_calculate_game_value_existing_doubles_combined_with_virgin(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    # 1 pre-existing double + 1 virgin → 2 doubles total → alone_price * 4
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    players: list[Player] = [player_1, player_2, player_3, player_4]

    player_2.collected_cards = []
    player_1.collected_cards = [MagicMock()]
    player_3.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]
    teams = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    distributer: MoneyDistributer = make_distributer(
        RamschMoneyDistributer,
        players=players,
        teams=teams,
        winners=[player_1, player_3, player_4],
        alone_price=20,
        amount_game_value_doubles=1,
    )
    assert distributer.calculate_game_value() == 80
