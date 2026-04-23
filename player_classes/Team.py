from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player_classes.Player import Player


class Team:
    def __init__(self, team_name: str) -> None:
        self.team_name = team_name
        self.players: list[Player] = []

    def __repr__(self) -> str:
        return self.team_name

    @property
    def points(self) -> int:
        return sum(player.points for player in self.players)
