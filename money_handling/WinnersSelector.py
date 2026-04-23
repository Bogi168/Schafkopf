from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player_classes.Team import Team
    from player_classes.Player import Player


class WinnersSelector:
    def __init__(self, teams: list[Team], active_team: Team | None) -> None:
        self.teams: list[Team] = teams
        self.active_team: Team | None = active_team

    def get_most_points_teams(self) -> list[Team]:
        most_point_teams: list[Team] = []
        most_point_team_points = 0
        for team in self.teams:
            if team.points > most_point_team_points:
                most_point_team_points = team.points
                most_point_teams.clear()
                most_point_teams.append(team)
            elif team.points == most_point_team_points:
                most_point_teams.append(team)
        return most_point_teams

    def get_game_winners(self) -> list[Player]:
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
    def __init__(self, teams: list[Team]) -> None:
        super().__init__(teams=teams, active_team=None)

    def get_game_winners(self) -> list[Player]:
        winners: list[Player] = []
        most_point_teams = self.get_most_points_teams()
        if len(most_point_teams) != 1:
            winners = [
                player
                for team in self.teams
                for player in team.players
                if team not in most_point_teams
            ]
        else:
            if most_point_teams[0].points >= 91:
                winners.append(most_point_teams[0].players[0])
            else:
                winners = [
                    player
                    for team in self.teams
                    for player in team.players
                    if team not in most_point_teams
                ]
        return winners
