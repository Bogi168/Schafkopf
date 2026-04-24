from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from player_classes.Player import Player


@dataclass
class Team:
    team_name: str
    players: list[Player] = field(default_factory=list)

    @property
    def points(self) -> int:
        return sum(player.points for player in self.players)
