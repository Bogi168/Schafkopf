from abc import ABC, abstractmethod
from Cards import Card
from Player import Team, Player


class MoneyDistributer(ABC):
    def __init__(
        self,
        base_price: int,
        call_price: int,
        alone_price: int,
        players: list[Player],
        teams: list[Team],
        amount_game_value_doublers: int,
    ) -> None:
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price
        self.players: list[Player] = players
        self.teams: list[Team] = teams
        self.amount_game_value_doublers: int = amount_game_value_doublers

    def get_players_team(self, player: Player) -> Team | None:
        player_team = None
        for team in self.teams:
            if player in team.players:
                player_team = team
        return player_team

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

    @abstractmethod
    def get_game_winners(self) -> list[Player]:
        pass

    @staticmethod
    def is_player_has_trump(player: Player, trump: Card) -> bool:
        return any(card == trump for card in player.player_cards)

    def is_team_has_trump(self, team_players: list[Player], trump: Card) -> bool:
        return any(
            self.is_player_has_trump(player=player, trump=trump)
            for player in team_players
        )

    def count_team_runners(self, team: Team, trumps: list[Card]) -> int:
        runners_count = 0
        for trump in trumps:
            if self.is_team_has_trump(team_players=team.players, trump=trump):
                runners_count += 1
            else:
                return runners_count
        return runners_count

    def count_game_runners(self, trumps: list[Card]):
        pass

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
    ) -> None:
        super().__init__(
            base_price=0,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            amount_game_value_doublers=amount_game_value_doublers,
        )

    def get_game_winners(self) -> list[Player]:
        winners: list[Player] = []
        most_point_teams = self.get_most_points_teams()
        if len(most_point_teams) != 1:
            for team in self.teams:
                if team not in most_point_teams:
                    for player in team.players:
                        winners.append(player)
        else:
            if most_point_teams[0].points >= 91:
                winners.append(most_point_teams[0].players[0])
            else:
                for team in self.teams:
                    if team not in most_point_teams:
                        for player in team.players:
                            winners.append(player)
        return winners

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
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=call_price,
            alone_price=0,
            players=players,
            teams=teams,
            amount_game_value_doublers=amount_game_value_doublers,
        )
        self.active_team: Team = active_team
        self.runners_amount: int = 0

    def get_game_winners(self) -> list[Player]:
        winners: list[Player] = []
        most_point_teams = self.get_most_points_teams()
        if len(most_point_teams) == 1:
            for team in most_point_teams:
                for player in team.players:
                    winners.append(player)
        else:
            winner_teams = [
                team for team in most_point_teams if self.active_team != team
            ]
            for team in winner_teams:
                for player in team.players:
                    winners.append(player)
        return winners

    def count_game_runners(self, trumps: list[Card]) -> int:
        minimum_runners: int = 3
        for team in self.teams:
            runners_count: int = self.count_team_runners(team=team, trumps=trumps)
            if runners_count >= minimum_runners:
                self.runners_amount = runners_count
                return runners_count
        self.runners_amount = 0
        return 0

    def calculate_game_value(self) -> int:
        black_threshold = 120
        schneider_threshold = 90
        game_value = 0
        game_value += self.call_price
        game_value += self.runners_amount * self.base_price
        winners: list[Player] = self.get_game_winners()
        winning_team = self.get_players_team(player=winners[0])

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


class WenzMoneyDistributer(MoneyDistributer):

    def __init__(
        self,
        base_price: int,
        alone_price: int,
        players: list[Player],
        teams: list[Team],
        amount_game_value_doublers: int,
        active_team: Team,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            amount_game_value_doublers=amount_game_value_doublers,
        )
        self.active_team: Team = active_team
        self.runners_amount: int = 0

    def get_game_winners(self) -> list[Player]:
        winners: list[Player] = []
        most_point_teams = self.get_most_points_teams()
        if len(most_point_teams) == 1:
            for team in most_point_teams:
                for player in team.players:
                    winners.append(player)
        else:
            winner_teams = [
                team for team in most_point_teams if self.active_team != team
            ]
            for team in winner_teams:
                for player in team.players:
                    winners.append(player)
        return winners

    def count_game_runners(self, trumps: list[Card]) -> int:
        minimum_runners: int = 2
        for team in self.teams:
            runners_count: int = self.count_team_runners(team=team, trumps=trumps)
            if runners_count >= minimum_runners:
                self.runners_amount = runners_count
                return runners_count
        self.runners_amount = 0
        return 0

    def calculate_game_value(self) -> int:
        black_threshold = 120
        schneider_threshold = 90
        game_value = 0
        game_value += self.alone_price
        game_value += self.runners_amount * self.base_price
        winners: list[Player] = self.get_game_winners()
        winning_team = self.get_players_team(player=winners[0])

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


class SoloMoneyDistributer(MoneyDistributer):

    def __init__(
        self,
        base_price: int,
        alone_price: int,
        players: list[Player],
        teams: list[Team],
        amount_game_value_doublers: int,
        active_team: Team,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=0,
            alone_price=alone_price,
            players=players,
            teams=teams,
            amount_game_value_doublers=amount_game_value_doublers,
        )
        self.active_team: Team = active_team
        self.runners_amount: int = 0

    def get_game_winners(self) -> list[Player]:
        winners: list[Player] = []
        most_point_teams = self.get_most_points_teams()
        if len(most_point_teams) == 1:
            for team in most_point_teams:
                for player in team.players:
                    winners.append(player)
        else:
            winner_teams = [
                team for team in most_point_teams if self.active_team != team
            ]
            for team in winner_teams:
                for player in team.players:
                    winners.append(player)
        return winners

    def count_game_runners(self, trumps: list[Card]) -> int:
        minimum_runners: int = 3
        for team in self.teams:
            runners_count: int = self.count_team_runners(team=team, trumps=trumps)
            if runners_count >= minimum_runners:
                self.runners_amount = runners_count
                return runners_count
        self.runners_amount = 0
        return 0

    def calculate_game_value(self) -> int:
        black_threshold = 120
        schneider_threshold = 90
        game_value = 0
        game_value += self.alone_price
        game_value += self.runners_amount * self.base_price
        winners: list[Player] = self.get_game_winners()
        winning_team = self.get_players_team(player=winners[0])

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
