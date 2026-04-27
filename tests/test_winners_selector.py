import pytest
from money_handling.WinnersSelector import WinnersSelector, RamschWinnersSelector
from player_classes.Player import Player
from player_classes.Team import Team
from system.Renderer import ConsoleRenderer
from input_validators.GameDecisionValidator import GameDecisionValidator


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
