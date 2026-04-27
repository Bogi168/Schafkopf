import pytest
from card_classes.Cards import Card, Type, Color
from money_handling.WinnersSelector import WinnersSelector, RamschWinnersSelector
from player_classes.Player import Player
from player_classes.Team import Team
from system.Renderer import ConsoleRenderer
from input_validators.GameDecisionValidator import GameDecisionValidator


@pytest.fixture
def eichel_ober():
    return Card(Color.EICHEL, Type.OBER)


@pytest.fixture
def gruen_ober():
    return Card(Color.GRUEN, Type.OBER)


@pytest.fixture
def herz_ober():
    return Card(Color.HERZ, Type.OBER)


@pytest.fixture
def schellen_ober():
    return Card(Color.SCHELLEN, Type.OBER)


@pytest.fixture
def eichel_unter():
    return Card(Color.EICHEL, Type.UNTER)


@pytest.fixture
def gruen_unter():
    return Card(Color.GRUEN, Type.UNTER)


@pytest.fixture
def herz_unter():
    return Card(Color.HERZ, Type.UNTER)


@pytest.fixture
def schellen_unter():
    return Card(Color.SCHELLEN, Type.UNTER)


@pytest.fixture
def eichel_sau():
    return Card(Color.EICHEL, Type.SAU)


@pytest.fixture
def eichel_ten():
    return Card(Color.EICHEL, Type.TEN)


@pytest.fixture
def eichel_koenig():
    return Card(Color.EICHEL, Type.KOENIG)


@pytest.fixture
def gruen_sau():
    return Card(Color.GRUEN, Type.SAU)


@pytest.fixture
def gruen_ten():
    return Card(Color.GRUEN, Type.TEN)


@pytest.fixture
def gruen_koenig():
    return Card(Color.GRUEN, Type.KOENIG)


@pytest.fixture
def herz_sau():
    return Card(Color.HERZ, Type.SAU)


@pytest.fixture
def herz_ten():
    return Card(Color.HERZ, Type.TEN)


@pytest.fixture
def herz_koenig():
    return Card(Color.HERZ, Type.KOENIG)


@pytest.fixture
def schellen_sau():
    return Card(Color.SCHELLEN, Type.SAU)


@pytest.fixture
def schellen_ten():
    return Card(Color.SCHELLEN, Type.TEN)


@pytest.fixture
def schellen_koenig():
    return Card(Color.SCHELLEN, Type.KOENIG)


@pytest.fixture
def all_cards(
    eichel_ober,
    eichel_unter,
    eichel_sau,
    eichel_ten,
    eichel_koenig,
    gruen_ober,
    gruen_unter,
    gruen_sau,
    gruen_ten,
    gruen_koenig,
    herz_ober,
    herz_unter,
    herz_sau,
    herz_ten,
    herz_koenig,
    schellen_ober,
    schellen_unter,
    schellen_sau,
    schellen_ten,
    schellen_koenig,
):
    return [
        eichel_ober,
        eichel_unter,
        eichel_sau,
        eichel_ten,
        eichel_koenig,
        gruen_ober,
        gruen_unter,
        gruen_sau,
        gruen_ten,
        gruen_koenig,
        herz_ober,
        herz_unter,
        herz_sau,
        herz_ten,
        herz_koenig,
        schellen_ober,
        schellen_unter,
        schellen_sau,
        schellen_ten,
        schellen_koenig,
    ]


@pytest.fixture
def test_player_1() -> Player:
    return Player(
        player_name="Testplayer 1",
        renderer=ConsoleRenderer(),
        game_decision_validator=GameDecisionValidator({}, {}),
    )


@pytest.fixture
def test_player_2() -> Player:
    return Player(
        player_name="Testplayer 2",
        renderer=ConsoleRenderer(),
        game_decision_validator=GameDecisionValidator({}, {}),
    )


@pytest.fixture
def test_player_3() -> Player:
    return Player(
        player_name="Testplayer 3",
        renderer=ConsoleRenderer(),
        game_decision_validator=GameDecisionValidator({}, {}),
    )


@pytest.fixture
def test_player_4() -> Player:
    return Player(
        player_name="Testplayer 4",
        renderer=ConsoleRenderer(),
        game_decision_validator=GameDecisionValidator({}, {}),
    )


@pytest.fixture
def team_alone_player_1(test_player_1) -> Team:
    team_alone_player = Team(team_name="TeamAlonePlayer1")
    team_alone_player.players = [test_player_1]
    return team_alone_player


@pytest.fixture
def team_alone_player_2(test_player_2) -> Team:
    team_alone_player = Team(team_name="TeamAlonePlayer2")
    team_alone_player.players = [test_player_2]
    return team_alone_player


@pytest.fixture
def team_alone_player_3(test_player_3) -> Team:
    team_alone_player = Team(team_name="TeamAlonePlayer3")
    team_alone_player.players = [test_player_3]
    return team_alone_player


@pytest.fixture
def team_alone_player_4(test_player_4) -> Team:
    team_alone_player = Team(team_name="TeamAlonePlayer4")
    team_alone_player.players = [test_player_4]
    return team_alone_player


@pytest.fixture
def team_three_players(test_player_2, test_player_3, test_player_4) -> Team:
    team_alone_player = Team(team_name="TeamThreePlayers")
    team_alone_player.players = [test_player_2, test_player_3, test_player_4]
    return team_alone_player


@pytest.fixture
def team_two_players_1(test_player_1, test_player_2) -> Team:
    team_two_players_1 = Team(team_name="TeamTwoPlayers1")
    team_two_players_1.players = [test_player_1, test_player_2]
    return team_two_players_1


@pytest.fixture
def team_two_players_2(test_player_3, test_player_4) -> Team:
    team_two_players_2 = Team(team_name="TeamTwoPlayers2")
    team_two_players_2.players = [test_player_3, test_player_4]
    return team_two_players_2


def test_alone_player(
    team_alone_player_1,
    team_three_players,
    eichel_sau,
    gruen_sau,
    herz_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
):
    team_three_players.players[0].player_cards = [eichel_sau, gruen_sau]
    team_three_players.players[1].player_cards = [herz_sau, schellen_sau]
    team_three_players.players[2].player_cards = [eichel_ten, gruen_ten]
    teams = [team_alone_player_1, team_three_players]
    winners_selector = WinnersSelector(teams=teams, active_team=team_alone_player_1)
    assert winners_selector.get_most_points_teams() == [team_three_players]
