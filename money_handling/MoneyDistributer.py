from __future__ import annotations
from typing import TYPE_CHECKING

from system.custom_exceptions import MoneyDistributionNotPossible

if TYPE_CHECKING:
    from player_classes.Player import Player


class MoneyDistributer:
    """An object that distributes money across multiple players."""

    def distribute_money(
        self, game_value: int, winners: list[Player], players: list[Player]
    ) -> None:
        """
        Distributes the money of the given game value to the given winners and deducts it from the losers
        :param game_value: The game value to distribute
        :type game_value: int
        :param winners: The winners of the game
        :type winners: list[Player]
        :param players: The players of the game
        :type players: list[Player]
        :rtype: None
        """

        losers: list[Player] = [loser for loser in players if loser not in winners]

        if not winners or len(winners) == len(players):
            return

        elif len(winners) == len(losers):
            for i in range(len(winners)):
                losers[i].money -= game_value
                winners[i].money += game_value

        elif len(winners) == 1:
            for loser in losers:
                loser.money -= game_value
                winners[0].money += game_value

        elif len(losers) == 1:
            for winner in winners:
                losers[0].money -= game_value
                winner.money += game_value

        else:
            raise MoneyDistributionNotPossible(
                "A clean money distribution is impossible"
            )


class RamschMoneyDistributer(MoneyDistributer):
    def distribute_money(
        self, game_value: int, winners: list[Player], players: list[Player]
    ) -> None:
        losers: list[Player] = [loser for loser in players if loser not in winners]

        if not winners or len(winners) == len(players):
            return

        elif len(winners) == len(losers):
            for i in range(len(winners)):
                losers[i].money -= game_value
                winners[i].money += game_value

        elif len(winners) == 1:
            for loser in losers:
                loser.money -= game_value
                winners[0].money += game_value

        elif len(losers) == 1:
            for winner in winners:
                losers[0].money += game_value
                winner.money += game_value

        elif len(winners) >= len(losers):
            money_per_loser: int = (
                ((game_value * len(losers)) // len(winners)) // len(losers)
            ) * len(winners)
            money_per_winner: int = money_per_loser * len(losers) // len(winners)
            for winner in winners:
                winner.money += game_value * len(losers)

        else:
            remainder_money_distribution = (game_value * len(losers)) % len(winners)
            if not remainder_money_distribution:
                money_per_loser: int = (game_value * len(losers)) // len(winners)
                money_per_winner: int = money_per_loser * len(losers) // len(winners)
            else:
                money_per_loser: int = (
                    ((game_value * len(losers)) // len(winners)) // len(losers)
                ) * len(winners)
                money_per_winner: int = money_per_loser * len(losers) // len(winners)

            for loser in losers:
                loser.money -= money_per_loser

            for winner in winners:
                winner.money += money_per_winner


class SauspielMoneyDistributer(MoneyDistributer):
    def distribute_money(
        self, game_value: int, winners: list[Player], players: list[Player]
    ) -> None:
        losers = [loser for loser in players if loser not in winners]
        for i in range(len(winners)):
            losers[i].money -= game_value
            winners[i].money += game_value


class AloneMoneyDistributer(MoneyDistributer):
    pass


class WenzMoneyDistributer(AloneMoneyDistributer):
    pass


class SoloMoneyDistributer(AloneMoneyDistributer):
    pass
