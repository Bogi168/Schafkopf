from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from system.custom_exceptions import PlayerHasNoTeamError

if TYPE_CHECKING:
    from player_classes.Team import Team
    from player_classes.Player import Player


class MoneyDistributer(ABC):
    """An object that distributes money across multiple players."""

    def __init__(
        self,
        base_price: int,
        call_price: int,
        alone_price: int,
        players: list[Player],
        teams: list[Team],
        active_team: Team | None,
        winners: list[Player],
        amount_game_value_doubles: int,
        runners_amount: int,
        amount_game_card_points: int,
    ) -> None:
        """
        :param base_price: base price for game value calculations
        :type base_price: int
        :param call_price: call price for game value calculations
        :type call_price: int
        :param alone_price: alone price for game value calculations
        :type alone_price: int
        :param players: A list of all the players of the game
        :type players: list[Player]
        :param teams: A list of all the teams of the game
        :type teams: list[Team]
        :param active_team: The active team of the game
        :type active_team: Team | None
        :param winners: The winners of the game
        :type winners: list[Player]
        :param amount_game_value_doubles: The amount of times someone decided to double the game value
        :type amount_game_value_doubles: int
        :param runners_amount: The amount of game runners
        :type runners_amount: int
        :param amount_game_card_points: The amount of points when combining all card points of a game
        :type amount_game_card_points: int
        """

        self.base_price: int = base_price
        self.call_price: int = call_price
        self.alone_price: int = alone_price
        self.players: list[Player] = players
        self.teams: list[Team] = teams
        self.active_team: Team | None = active_team
        self.winners: list[Player] = winners
        self.amount_game_value_doubles: int = amount_game_value_doubles
        self.runners_amount: int = runners_amount
        self.schneider_threshold: int = amount_game_card_points - (
            amount_game_card_points // 4
        )
        self.black_threshold: int = amount_game_card_points

    def get_players_team(self, player: Player) -> Team:
        """
        Returns the team of a given player.
        :param player: The player for whose team is to be returned
        :type player: Player
        :return: The player's team
        :rtype: Team
        """

        for team in self.teams:
            if player in team.players:
                return team
        else:
            raise PlayerHasNoTeamError(f"{player} has no team!")

    def basic_game_value_adds(self, game_value: int) -> int:
        """
        Adds runners, schneider and black values to the given game value if needed
        and doubles game value for the amount of times it got doubled by players.
        :param game_value: The previous game value
        :type game_value: int
        :return: The updated game value
        :rtype: int
        """

        game_value += self.runners_amount * self.base_price

        winning_team: Team = self.get_players_team(player=self.winners[0])

        if winning_team.points > self.schneider_threshold or (
            winning_team.points == self.schneider_threshold
            and self.active_team != winning_team
        ):
            game_value += self.base_price

        if winning_team.points == self.black_threshold:
            game_value += self.base_price

        for _ in range(self.amount_game_value_doubles):
            game_value *= 2

        return game_value

    @abstractmethod
    def calculate_game_value(self) -> int:
        """calculates the game value for the whole game"""
        pass

    def distribute_money(self, game_value: int, winners: list[Player]) -> None:
        """
        Distributes the money of the given game value to the given winners and deducts it from the losers
        :param game_value: The game value to distribute
        :type game_value: int
        :param winners: The winners of the game
        :type winners: list[Player]
        """

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
        amount_game_value_doubles: int,
        winners: list[Player],
        amount_game_card_points: int,
    ) -> None:
        super().__init__(
            base_price=0,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            active_team=None,
            amount_game_value_doubles=amount_game_value_doubles,
            winners=winners,
            runners_amount=0,
            amount_game_card_points=amount_game_card_points,
        )

    def count_virgins(self) -> int:
        """
        :return: The amount of players who didn't collect any cards during the game
        """

        virgins_count = 0
        for player in self.players:
            if not player.collected_cards:
                virgins_count += 1
        return virgins_count

    def calculate_game_value(self) -> int:
        game_value = self.alone_price

        for _ in range(self.count_virgins()):
            self.amount_game_value_doubles += 1

        for _ in range(self.amount_game_value_doubles):
            game_value *= 2
        return game_value


class SauspielMoneyDistributer(MoneyDistributer):

    def __init__(
        self,
        base_price: int,
        call_price: int,
        players: list[Player],
        teams: list[Team],
        amount_game_value_doubles: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
        amount_game_card_points: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=call_price,
            alone_price=0,
            players=players,
            teams=teams,
            amount_game_value_doubles=amount_game_value_doubles,
            active_team=active_team,
            winners=winners,
            runners_amount=runners_amount,
            amount_game_card_points=amount_game_card_points,
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
        amount_game_value_doubles: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
        amount_game_card_points: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            active_team=active_team,
            amount_game_value_doubles=amount_game_value_doubles,
            winners=winners,
            runners_amount=runners_amount,
            amount_game_card_points=amount_game_card_points,
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
        amount_game_value_doubles: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
        amount_game_card_points: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            active_team=active_team,
            amount_game_value_doubles=amount_game_value_doubles,
            winners=winners,
            runners_amount=runners_amount,
            amount_game_card_points=amount_game_card_points,
        )

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.alone_price
        game_value = self.basic_game_value_adds(game_value=game_value)
        return game_value
