from money_handling.WinnersSelector import WinnersSelector, RamschWinnersSelector


def test_alone_most_points_teams(
    team_alone_player_1,
    team_three_players,
    eichel_sau,
    gruen_sau,
    herz_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
    herz_ten,
    schellen_ten,
    eichel_koenig,
    gruen_koenig,
    herz_koenig,
    schellen_koenig,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
):
    teams = [team_alone_player_1, team_three_players]
    winners_selector = WinnersSelector(teams=teams, active_team=team_alone_player_1)

    team_three_players.players[0].collected_cards = [
        eichel_sau,
        schellen_ten,
        schellen_sau,
        eichel_ten,
    ]
    team_three_players.players[1].collected_cards = [gruen_sau]
    team_three_players.players[2].collected_cards = [herz_sau]
    team_alone_player_1.players[0].collected_cards = [
        gruen_ten,
        herz_ten,
        eichel_koenig,
    ]

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted([team_three_players], key=lambda x: x.team_name)

    team_three_players.players[0].collected_cards = []
    team_three_players.players[1].collected_cards = []
    team_three_players.players[2].collected_cards = []
    team_alone_player_1.players[0].collected_cards = [eichel_sau]

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted([team_alone_player_1], key=lambda x: x.team_name)

    team_three_players.players[0].collected_cards = [
        eichel_sau,
        gruen_sau,
        herz_sau,
        schellen_sau,
    ]
    team_three_players.players[1].collected_cards = [
        eichel_ten,
        eichel_koenig,
        eichel_unter,
    ]
    team_three_players.players[2].collected_cards = []
    team_alone_player_1.players[0].collected_cards = [
        gruen_ten,
        herz_ten,
        schellen_ten,
        gruen_koenig,
        herz_koenig,
        schellen_koenig,
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        gruen_unter,
        herz_unter,
        schellen_unter,
    ]

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted(
        [
            team_alone_player_1,
            team_three_players,
        ],
        key=lambda x: x.team_name,
    )


def test_duo_most_points_teams(
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    gruen_sau,
    herz_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
    herz_ten,
    schellen_ten,
    eichel_koenig,
    gruen_koenig,
    herz_koenig,
    schellen_koenig,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
):
    teams = [team_two_players_1, team_two_players_2]
    winners_selector = WinnersSelector(teams=teams, active_team=team_two_players_1)

    team_two_players_1.players[0].collected_cards = [
        eichel_sau,
        schellen_ten,
        schellen_sau,
        eichel_ten,
    ]
    team_two_players_1.players[1].collected_cards = [gruen_sau]
    team_two_players_2.players[0].collected_cards = [herz_sau]
    team_two_players_2.players[1].collected_cards = [
        gruen_ten,
        herz_ten,
        eichel_koenig,
    ]

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted([team_two_players_1], key=lambda x: x.team_name)

    team_two_players_1.players[0].collected_cards = []
    team_two_players_1.players[1].collected_cards = []
    team_two_players_2.players[0].collected_cards = []
    team_two_players_2.players[1].collected_cards = [eichel_sau]

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted([team_two_players_2], key=lambda x: x.team_name)

    team_two_players_1.players[0].collected_cards = [
        eichel_sau,
        gruen_sau,
        herz_sau,
        schellen_sau,
    ]
    team_two_players_1.players[1].collected_cards = [
        eichel_ten,
        eichel_koenig,
        eichel_unter,
    ]
    team_two_players_2.players[0].collected_cards = [
        gruen_ten,
        herz_ten,
        schellen_ten,
        gruen_koenig,
        herz_koenig,
        schellen_koenig,
    ]
    team_two_players_2.players[1].collected_cards = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        gruen_unter,
        herz_unter,
        schellen_unter,
    ]

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted(
        [
            team_two_players_1,
            team_two_players_2,
        ],
        key=lambda x: x.team_name,
    )


def test_alone_get_game_winners(
    team_alone_player_1,
    team_three_players,
    eichel_sau,
    gruen_sau,
    herz_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
    herz_ten,
    schellen_ten,
    eichel_koenig,
    gruen_koenig,
    herz_koenig,
    schellen_koenig,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
):
    teams = [team_alone_player_1, team_three_players]
    winners_selector = WinnersSelector(teams=teams, active_team=team_alone_player_1)

    team_three_players.players[0].collected_cards = [
        eichel_sau,
        schellen_ten,
        schellen_sau,
        eichel_ten,
    ]
    team_three_players.players[1].collected_cards = [gruen_sau]
    team_three_players.players[2].collected_cards = [herz_sau]
    team_alone_player_1.players[0].collected_cards = [
        gruen_ten,
        herz_ten,
        eichel_koenig,
    ]

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_three_players.players], key=lambda x: x.player_name
    )

    team_three_players.players[0].collected_cards = []
    team_three_players.players[1].collected_cards = []
    team_three_players.players[2].collected_cards = []
    team_alone_player_1.players[0].collected_cards = [eichel_sau]

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted([team_alone_player_1.players[0]], key=lambda x: x.player_name)

    team_three_players.players[0].collected_cards = [
        eichel_sau,
        gruen_sau,
        herz_sau,
        schellen_sau,
    ]
    team_three_players.players[1].collected_cards = [
        eichel_ten,
        eichel_koenig,
        eichel_unter,
    ]
    team_three_players.players[2].collected_cards = []
    team_alone_player_1.players[0].collected_cards = [
        gruen_ten,
        herz_ten,
        schellen_ten,
        gruen_koenig,
        herz_koenig,
        schellen_koenig,
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        gruen_unter,
        herz_unter,
        schellen_unter,
    ]

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_three_players.players], key=lambda x: x.player_name
    )


def test_duo_get_game_winners(
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    gruen_sau,
    herz_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
    herz_ten,
    schellen_ten,
    eichel_koenig,
    gruen_koenig,
    herz_koenig,
    schellen_koenig,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
):
    teams = [team_two_players_1, team_two_players_2]
    winners_selector = WinnersSelector(teams=teams, active_team=team_two_players_1)

    team_two_players_1.players[0].collected_cards = [
        eichel_sau,
        schellen_ten,
        schellen_sau,
        eichel_ten,
    ]
    team_two_players_1.players[1].collected_cards = [gruen_sau]
    team_two_players_2.players[0].collected_cards = [herz_sau]
    team_two_players_2.players[1].collected_cards = [
        gruen_ten,
        herz_ten,
        eichel_koenig,
    ]

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_two_players_1.players], key=lambda x: x.player_name
    )

    team_two_players_1.players[0].collected_cards = []
    team_two_players_1.players[1].collected_cards = []
    team_two_players_2.players[0].collected_cards = []
    team_two_players_2.players[1].collected_cards = [eichel_sau]

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_two_players_2.players], key=lambda x: x.player_name
    )

    team_two_players_1.players[0].collected_cards = [
        eichel_sau,
        gruen_sau,
        herz_sau,
        schellen_sau,
    ]
    team_two_players_1.players[1].collected_cards = [
        eichel_ten,
        eichel_koenig,
        eichel_unter,
    ]
    team_two_players_2.players[0].collected_cards = [
        gruen_ten,
        herz_ten,
        schellen_ten,
        gruen_koenig,
        herz_koenig,
        schellen_koenig,
    ]
    team_two_players_2.players[1].collected_cards = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        gruen_unter,
        herz_unter,
        schellen_unter,
    ]

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_two_players_2.players], key=lambda x: x.player_name
    )


# special rules for Ramsch
def test_ramsch_one_loser(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
    eichel_sau,
    gruen_sau,
    herz_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
    herz_ten,
    schellen_ten,
    eichel_koenig,
):
    teams = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_2.players[0]],
    )

    team_alone_player_1.players[0].collected_cards = [
        eichel_sau,
        schellen_ten,
        schellen_sau,
        eichel_ten,
    ]
    team_alone_player_2.players[0].collected_cards = [gruen_sau]
    team_alone_player_3.players[0].collected_cards = [herz_sau]
    team_alone_player_4.players[0].collected_cards = [
        gruen_ten,
        herz_ten,
        eichel_koenig,
    ]

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1
        ],
        key=lambda x: x.player_name,
    )


def test_ramsch_one_winner(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
    eichel_sau,
    gruen_sau,
    herz_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
    herz_ten,
    schellen_ten,
    eichel_koenig,
    eichel_ober,
):
    teams = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_2.players[0]],
    )

    team_alone_player_1.players[0].collected_cards = [
        eichel_sau,
        gruen_sau,
        herz_sau,
        schellen_sau,
        eichel_ten,
        gruen_ten,
        herz_ten,
        schellen_ten,
        eichel_koenig,
        eichel_ober,
    ]
    team_alone_player_2.players[0].collected_cards = []
    team_alone_player_3.players[0].collected_cards = []
    team_alone_player_4.players[0].collected_cards = []

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted([team_alone_player_1.players[0]], key=lambda x: x.player_name)


def test_ramsch_two_most_point_teams(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
    eichel_sau,
    gruen_sau,
    herz_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
    herz_ten,
    schellen_ten,
    eichel_koenig,
    gruen_koenig,
    schellen_koenig,
):
    teams = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_2.players[0]],
    )

    team_alone_player_1.players[0].collected_cards = [
        eichel_sau,
        schellen_ten,
        schellen_sau,
    ]
    team_alone_player_2.players[0].collected_cards = [
        gruen_sau,
        herz_sau,
        gruen_ten,
    ]
    team_alone_player_3.players[0].collected_cards = [eichel_ten, herz_ten]
    team_alone_player_4.players[0].collected_cards = [eichel_koenig]

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1 and team != team_alone_player_2
        ],
        key=lambda x: x.player_name,
    )

    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_3.players[0], team_alone_player_4.players[0]],
    )

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1 and team != team_alone_player_2
        ],
        key=lambda x: x.player_name,
    )

    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_4.players[0]],
    )

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1
        ],
        key=lambda x: x.player_name,
    )

    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[],
    )

    team_alone_player_1.players[0].collected_cards = [
        eichel_sau,
        schellen_ten,
        schellen_sau,
    ]
    team_alone_player_2.players[0].collected_cards = [
        gruen_sau,
        herz_sau,
        gruen_ten,
    ]
    team_alone_player_3.players[0].collected_cards = [
        eichel_ten,
        herz_ten,
        eichel_koenig,
        gruen_koenig,
        schellen_koenig,
    ]
    team_alone_player_4.players[0].collected_cards = []

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_alone_player_4.players],
        key=lambda x: x.player_name,
    )

    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_4.players[0]],
    )

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1
        ],
        key=lambda x: x.player_name,
    )
