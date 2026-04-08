from Player import Player


class Team:
    def __init__(self, team_name: str) -> None:
        self.team_name = team_name
        self.players: list[Player] = []

    def __repr__(self) -> str:
        return self.team_name

    @property
    def points(self) -> int:
        points = 0
        for player in self.players:
            points += player.points
        return points
