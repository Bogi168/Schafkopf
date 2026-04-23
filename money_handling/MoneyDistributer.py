from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from system.custom_exceptions import PlayerHasNoTeamError

if TYPE_CHECKING:
    from player_classes.Team import Team
    from player_classes.Player import Player


class MoneyDistributer(ABC):
    def __init__(
        self,
        base_price: int,
        call_price: int,
        alone_price: int,
        players: list[Player],
        teams: list[Team],
        active_team: Team | None,
        winners: list[Player],
        amount_game_value_doublers: int,
        runners_amount: int,
    ) -> None:
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price
        self.players: list[Player] = players
        self.teams: list[Team] = teams
        self.active_team: Team | None = active_team
        self.winners: list[Player] = winners
        self.amount_game_value_doublers: int = amount_game_value_doublers
        self.runners_amount: int = runners_amount

    def get_players_team(self, player: Player) -> Team:
        for team in self.teams:
            if player in team.players:
                return team
        else:
            raise PlayerHasNoTeamError(f"{player} has no team!")

    def basic_game_value_adds(self, game_value: int) -> int:
        black_threshold = 120
        schneider_threshold = 90

        game_value += self.runners_amount * self.base_price

        winning_team: Team = self.get_players_team(player=self.winners[0])

        if winning_team.points > schneider_threshold or (
            winning_team.points == schneider_threshold
            and self.active_team != winning_team
        ):
            game_value += self.base_price

        if winning_team.points == black_threshold:
            game_value += self.base_price

        for _ in range(self.amount_game_value_doublers):
            game_value *= 2

        return game_value

    @abstractmethod
    def calculate_game_value(self) -> int:
        pass

    def distribute_money(self, game_value: int, winners: list[Player]) -> None:
        losers = [loser for loser in self.players if loser not in winners]
        if len(winners) == 1:
            for index in range(len(losers)):
                losers[index].money -= game_value
                winners[0].money += game_value
        elif len(winners) == 2:
            for index in range(len(winners)):
                losers[index].money -= game_value
                winners[index].money += game_value
        elif len(winners) == 3:
            for index in range(len(winners)):
                losers[0].money -= game_value
                winners[index].money += game_value


class RamschMoneyDistributer(MoneyDistributer):
    def __init__(
        self,
        alone_price: int,
        players: list[Player],
        teams: list[Team],
        amount_game_value_doublers: int,
        winners: list[Player],
    ) -> None:
        super().__init__(
            base_price=0,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            active_team=None,
            amount_game_value_doublers=amount_game_value_doublers,
            winners=winners,
            runners_amount=0,
        )

    def count_virgins(self) -> int:
        virgins_count = 0
        for player in self.players:
            if len(player.collected_cards) == 0:
                virgins_count += 1
        return virgins_count

    def calculate_game_value(self) -> int:
        game_value = self.alone_price
        virgins_count = self.count_virgins()

        for x in range(virgins_count):
            game_value *= 2

        for _ in range(self.amount_game_value_doublers):
            game_value *= 2
        return game_value


class SauspielMoneyDistributer(MoneyDistributer):

    def __init__(
        self,
        base_price: int,
        call_price: int,
        players: list[Player],
        teams: list[Team],
        amount_game_value_doublers: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=call_price,
            alone_price=0,
            players=players,
            teams=teams,
            amount_game_value_doublers=amount_game_value_doublers,
            active_team=active_team,
            winners=winners,
            runners_amount=runners_amount,
        )

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.call_price
        game_value = self.basic_game_value_adds(game_value=game_value)
        return game_value


class WenzMoneyDistributer(MoneyDistributer):

    def __init__(
        self,
        base_price: int,
        alone_price: int,
        players: list[Player],
        teams: list[Team],
        amount_game_value_doublers: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            active_team=active_team,
            amount_game_value_doublers=amount_game_value_doublers,
            winners=winners,
            runners_amount=runners_amount,
        )

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.alone_price
        game_value = self.basic_game_value_adds(game_value=game_value)
        return game_value


class SoloMoneyDistributer(MoneyDistributer):

    def __init__(
        self,
        base_price: int,
        alone_price: int,
        players: list[Player],
        teams: list[Team],
        amount_game_value_doublers: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            active_team=active_team,
            amount_game_value_doublers=amount_game_value_doublers,
            winners=winners,
            runners_amount=runners_amount,
        )

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.alone_price
        game_value = self.basic_game_value_adds(game_value=game_value)
        return game_value
