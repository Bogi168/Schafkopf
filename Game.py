from abc import ABC, abstractmethod
from Cards import Cards, Card, Type, Color
from Player import Player
from Renderer import Renderer
from Team import Team
from Card_Power_Calculator import (
    Card_Power_Calculator,
    Ramsch_Card_Power_Calculator,
    Sauspiel_Card_Power_Calculator,
    Wenz_Card_Power_Calculator,
    Solo_Card_Power_Calculator,
)
from Card_Decision_Validator import (
    Card_Decision_Validator,
    Ramsch_Card_Decision_Validator,
    Sauspiel_Card_Decision_Validator,
    Wenz_Card_Decision_Validator,
    Solo_Card_Decision_Validator,
)


class Game(ABC):
    rank = 0

    def __init__(
        self,
        trump_color: Color | None,
        trump_types: list[Type],
        cards: Cards,
        renderer: Renderer,
        card_power_calculator: Card_Power_Calculator,
        card_decision_validator: Card_Decision_Validator,
        players: list[Player],
        game_chooser: Player | None,
        base_price: int,
        call_price: int,
        alone_price: int,
    ) -> None:
        self.trump_color = trump_color
        self.trump_types = trump_types
        self.cards = cards
        self.renderer = renderer
        self.card_power_calculator = card_power_calculator
        self.card_decision_validator = card_decision_validator
        self.players = players
        self.game_chooser = game_chooser
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price

        self.runners_amount = 0
        self.winners: list[Player] = []
        self.teams: list[Team] = []

        self.trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in trump_types
            or (trump_color is not None and card.card_color == trump_color)
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        self.played_cards: list[Card] = []

    @property
    def lead_card(self) -> Card | None:
        if self.played_cards:
            return self.played_cards[0]
        else:
            return None

    @abstractmethod
    def create_teams(self) -> None:
        pass

    def sort_players(self, starter: Player) -> None:
        found_beginner = False
        while not found_beginner:
            player = self.players[0]
            if not player == starter:
                self.players.append(player)
                self.players.pop(0)
            else:
                found_beginner = True

    def find_players_team(self, player: Player) -> Team | None:
        player_team = None
        for team in self.teams:
            if player in team.players:
                player_team = team
        return player_team

    def sort_player_hands(self):
        for player in self.players:
            player.player_cards.sort(
                key=self.card_power_calculator.get_card_power, reverse=True
            )

    def play_round(self) -> None:
        for player in self.players:
            player.card_decision(
                renderer=self.renderer,
                played_cards=self.played_cards,
                move_validator=lambda d, p=player: self.card_decision_validator.is_move_legal(
                    player=p, decision=d, trumps=self.trumps, lead_card=self.lead_card
                ),
            )
            print(f"The played cards are: {self.played_cards}")
        strongest_card = self.card_power_calculator.get_strongest_played_card(
            played_cards=self.played_cards, trumps=self.trumps
        )
        winner_index = self.played_cards.index(strongest_card)
        for card in self.played_cards:
            self.players[winner_index].collected_cards.append(card)
        print(
            f"{self.players[winner_index].player_name} collected {self.players[winner_index].collected_cards[-4:]}"
            + "\n" * 2
        )
        starter = self.players[winner_index]
        self.sort_players(starter=starter)
        self.played_cards.clear()

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
        print(f"The most point teams are: {most_point_teams}")
        for team in most_point_teams:
            print(f"{team.team_name} has {team.points} points")
        return most_point_teams

    @staticmethod
    def is_multiple_most_point_teams(most_point_teams: list[Team]) -> bool:
        return len(most_point_teams) != 1

    def identify_game_winners(self) -> list[Player]:
        most_point_teams = self.get_most_points_teams()
        winners: list[Player] = []
        if not self.is_multiple_most_point_teams(most_point_teams=most_point_teams):
            for team in most_point_teams:
                for player in team.players:
                    winners.append(player)
        else:
            winner_teams = [
                team
                for team in most_point_teams
                if self.game_chooser not in team.players
            ]
            for team in winner_teams:
                for player in team.players:
                    winners.append(player)
        return winners

    @staticmethod
    def is_player_has_trump(player: Player, trump: Card) -> bool:
        for card in player.player_cards:
            if card == trump:
                return True
        return False

    def is_team_has_trump(self, team_players: list[Player], trump: Card) -> bool:
        for player in team_players:
            if self.is_player_has_trump(player=player, trump=trump):
                return True
        return False

    def count_team_runners(self, team: Team) -> int:
        runners_count = 0
        for trump in self.trumps:
            if self.is_team_has_trump(team_players=team.players, trump=trump):
                runners_count += 1
            else:
                return runners_count
        return runners_count

    def count_game_runners(self, minimum_runners: int = 3) -> int:
        for team in self.teams:
            runners_count = self.count_team_runners(team=team)
            if runners_count >= minimum_runners:
                return runners_count
        return 0

    @abstractmethod
    def calculate_game_value(self) -> int:
        pass

    def distribute_money(self, game_value: int) -> None:
        losers = [loser for loser in self.players if loser not in self.winners]
        if len(self.winners) == 1:
            for index in range(len(losers)):
                losers[index].money -= game_value
                self.winners[0].money += game_value
        elif len(self.winners) == 2:
            for index in range(len(self.winners)):
                losers[index].money -= game_value
                self.winners[index].money += game_value
        elif len(self.winners) == 3:
            for index in range(len(self.winners)):
                losers[0].money -= game_value
                self.winners[index].money += game_value

    def play_game(self) -> None:
        self.sort_player_hands()
        self.create_teams()
        self.runners_amount = self.count_game_runners()
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round()
        self.winners = self.identify_game_winners()
        game_value = self.calculate_game_value()
        self.distribute_money(game_value=game_value)
        print(f"The game winners are: {self.winners}")
        for player in self.players:
            print(f"{player} has {player.money} cents")


class Ramsch(Game):
    rank = 0.5

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player | None,
        base_price: int,
        call_price: int,
        alone_price: int,
    ) -> None:
        super().__init__(
            trump_color=Color.HERZ,
            trump_types=[Type.OBER, Type.UNTER],
            cards=cards,
            renderer=renderer,
            card_power_calculator=Ramsch_Card_Power_Calculator(),
            card_decision_validator=Ramsch_Card_Decision_Validator(),
            players=players,
            game_chooser=game_chooser,
            base_price=base_price,
            call_price=call_price,
            alone_price=alone_price,
        )

    def create_teams(self) -> None:
        for index in range(len(self.players)):
            team = Team(team_name=f"Team {index + 1}")
            team.players.append(self.players[index])
            self.teams.append(team)

    def identify_game_winners(self) -> list[Player]:
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
        return game_value


class Sauspiel(Game):
    rank = 1

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        sau_color: Color,
        game_chooser: Player | None,
        base_price: int,
        call_price: int,
        alone_price: int,
    ) -> None:
        super().__init__(
            trump_color=Color.HERZ,
            trump_types=[Type.OBER, Type.UNTER],
            cards=cards,
            renderer=renderer,
            card_power_calculator=Sauspiel_Card_Power_Calculator(),
            card_decision_validator=Sauspiel_Card_Decision_Validator(
                call_sau=[
                    card
                    for card in cards.full_deck
                    if card.card_color == sau_color and card.card_type == Type.SAU
                ][0]
            ),
            players=players,
            game_chooser=game_chooser,
            base_price=base_price,
            call_price=call_price,
            alone_price=alone_price,
        )
        self.sau_color = sau_color

    @property
    def call_sau(self) -> Card | None:
        for card in self.cards.full_deck:
            if card.card_color == self.sau_color and card.card_type == Type.SAU:
                return card
        return None

    def create_teams(self) -> None:
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        for player in self.players:
            for card in player.player_cards:
                if card == self.call_sau:
                    team_1.players.append(player)
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

    def calculate_game_value(self) -> int:
        black_threshold = 120
        schneider_threshold = 90
        game_value = 0
        game_value += self.call_price
        game_value += self.runners_amount * self.base_price
        winning_team = self.find_players_team(player=self.winners[0])

        if winning_team.points > schneider_threshold or (
            winning_team.points == schneider_threshold
            and self.game_chooser not in winning_team.players
        ):
            game_value += self.base_price

        if winning_team.points == black_threshold:
            game_value += self.base_price

        return game_value


class Wenz(Game):
    rank = 2

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player | None,
        base_price: int,
        call_price: int,
        alone_price: int,
    ) -> None:
        super().__init__(
            trump_color=None,
            trump_types=[Type.UNTER],
            cards=cards,
            renderer=renderer,
            card_power_calculator=Wenz_Card_Power_Calculator(),
            card_decision_validator=Wenz_Card_Decision_Validator(),
            players=players,
            game_chooser=game_chooser,
            base_price=base_price,
            call_price=call_price,
            alone_price=alone_price,
        )

    def create_teams(self) -> None:
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

    def count_game_runners(self, minimum_runners: int = 2) -> int:
        return super().count_game_runners(minimum_runners=minimum_runners)

    def calculate_game_value(self) -> int:
        black_threshold = 120
        schneider_threshold = 90
        game_value = 0
        game_value += self.alone_price
        game_value += self.runners_amount * self.base_price
        winning_team = self.find_players_team(player=self.winners[0])

        if winning_team.points > schneider_threshold or (
            winning_team.points == schneider_threshold
            and self.game_chooser not in winning_team.players
        ):
            game_value += self.base_price

        if winning_team.points == black_threshold:
            game_value += self.base_price

        return game_value


class Solo(Game):
    rank = 3

    def __init__(
        self,
        trump_color: Color,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player | None,
        base_price: int,
        call_price: int,
        alone_price: int,
    ) -> None:
        super().__init__(
            trump_color=trump_color,
            trump_types=[Type.OBER, Type.UNTER],
            cards=cards,
            renderer=renderer,
            card_power_calculator=Solo_Card_Power_Calculator(trump_color=trump_color),
            card_decision_validator=Solo_Card_Decision_Validator(),
            players=players,
            game_chooser=game_chooser,
            base_price=base_price,
            call_price=call_price,
            alone_price=alone_price,
        )

    def create_teams(self) -> None:
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

    def calculate_game_value(self) -> int:
        black_threshold = 120
        schneider_threshold = 90
        game_value = 0
        game_value += self.alone_price
        game_value += self.runners_amount * self.base_price
        winning_team = self.find_players_team(player=self.winners[0])

        if winning_team.points > schneider_threshold or (
            winning_team.points == schneider_threshold
            and self.game_chooser not in winning_team.players
        ):
            game_value += self.base_price

        if winning_team.points == black_threshold:
            game_value += self.base_price

        return game_value
