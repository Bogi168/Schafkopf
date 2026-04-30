from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player_classes.Team import Team
    from player_classes.Player import Player


class WinnersSelector:
    """Selects the winners of a game"""

    def __init__(self, teams: list[Team], active_team: Team | None) -> None:
        """
        :param teams: list of all the teams of a game
        :type teams: list[Team]
        :param active_team: The active team of the game
        :type active_team: Team | None
        """
        self.teams: list[Team] = teams
        self.active_team: Team | None = active_team

    def get_most_points_teams(self) -> list[Team]:
        """
        :return: A list of the teams with the most points
        :rtype: list[Team]
        """
        most_point_team_points = max(team.points for team in self.teams)
        most_point_teams: list[Team] = [
            team for team in self.teams if team.points == most_point_team_points
        ]
        return most_point_teams

    def get_game_winners(self) -> list[Player]:
        """
        :return: A list of the winners of the game
        :rtype: list[Player]
        """
        most_point_teams = self.get_most_points_teams()
        if len(most_point_teams) == 1:
            winners = [player for team in most_point_teams for player in team.players]
        else:
            winners = [
                player
                for team in most_point_teams
                if self.active_team != team
                for player in team.players
            ]
        return winners


class RamschWinnersSelector(WinnersSelector):
    def __init__(self, teams: list[Team], active_players: list[Player]) -> None:
        super().__init__(teams=teams, active_team=None)
        self.run_through_threshold = 91
        self.active_players: list[Player] = active_players

    def get_game_winners(self) -> list[Player]:
        winners: list[Player] = []
        most_point_teams = self.get_most_points_teams()
        if len(most_point_teams) > 1:
            winners = [
                player
                for team in self.teams
                for player in team.players
                if team not in most_point_teams
            ]
            losers = [
                player
                for team in self.teams
                for player in team.players
                if player not in winners
            ]
            if any(loser in self.active_players for loser in losers) and any(
                loser not in self.active_players for loser in losers
            ):
                for loser in losers:
                    if loser not in self.active_players:
                        winners.append(loser)

        else:
            if most_point_teams[0].points >= self.run_through_threshold:
                winners.append(most_point_teams[0].players[0])
            else:
                winners = [
                    player
                    for team in self.teams
                    for player in team.players
                    if team not in most_point_teams
                ]
        return winners
