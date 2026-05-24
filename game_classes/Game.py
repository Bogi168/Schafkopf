from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from game_classes.GameRenderer import GameRenderer
from game_classes.RoundManager import RoundManager
from money_handling.WinnersSelector import WinnersSelector
from player_classes.Team import Team
from card_classes.Cards import Card, Type, Color
from game_classes.RunnersCalculator import (
    RunnersCalculator,
)
from card_classes.CardPowerCalculator import CardPowerCalculator
from input_validators.CardDecisionValidator import CardDecisionValidator

from money_handling.MoneyDistributer import MoneyDistributer

if TYPE_CHECKING:
    from player_classes.Player import Player
    from system.Renderer import Renderer
    from card_classes.Cards import Cards
    from player_classes.TeamBuilder import TeamSetup, TeamBuilder
    from game_classes.RunnersCalculator import RunnersSetup


class Game(ABC):
    """An object that represents the game"""

    name = "Game"
    rank = 0
    is_choosable = False
    game_mapping: list[dict[str, Any]] = []

    def __init_subclass__(cls):
        super().__init_subclass__()
        class_map: dict[str, Any] = dict()
        class_map["name"] = cls.name
        class_map["rank"] = cls.rank
        class_map["is_choosable"] = cls.is_choosable
        class_map["class"] = cls
        Game.game_mapping.append(class_map)

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        team_builder: TeamBuilder,
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        runners_calculator: type[RunnersCalculator],
        trump_types: list[Type],
        trump_color: Color | None,
        players: list[Player],
        amount_game_value_doubles: int,
    ) -> None:
        """
        :param cards: An object which saves a full deck of cards and provides a deck to play with
        :type cards: Cards
        :param renderer: An object which renders information
        :type renderer: Renderer
        :param card_power_calculator: An object which calculates the card power
        :type card_power_calculator: CardPowerCalculator
        :param players: A list of objects which represent the players
        :type players: list[Player]
        :param amount_game_value_doubles: The amount of players who doubled the game value
        :type amount_game_value_doubles: int
        """

        self.cards: Cards = cards
        self.team_builder: TeamBuilder = team_builder
        self.card_power_calculator: CardPowerCalculator = card_power_calculator
        self.card_decision_validator: CardDecisionValidator = card_decision_validator
        self.runners_calculator: type[RunnersCalculator] = runners_calculator
        self.game_renderer: GameRenderer = GameRenderer(renderer=renderer)
        self.amount_game_value_doubles: int = amount_game_value_doubles
        self.players: list[Player] = players
        self.trumps: list[Card] = [
            card
            for card in cards.full_deck
            if card.card_type in trump_types or card.card_color == trump_color
        ]
        self.trumps.sort(key=card_power_calculator.get_card_power, reverse=True)
        self.round_manager: RoundManager | None = None
        self.total_card_points: int = sum(
            card.card_type.points for card in cards.full_deck
        )
        self.player_teams: dict[Player, Team] = dict()
        self.teams: list[Team] = []
        self.active_team: Team | None = None
        self.runners_amount: int = 0

    def create_teams(self) -> None:
        """
        Creates the team objects and sets player_teams, active_team and teams of Game
        :rtype: None
        """
        teams_setup: TeamSetup = self.team_builder.create_teams()
        self.player_teams: dict[Player, Team] = teams_setup.player_teams
        self.active_team: Team = teams_setup.active_team
        self.teams: list[Team] = teams_setup.teams

    def create_round_manager(self) -> RoundManager:
        """
        Creates a round manager object.
        :return: A round manager object
        :rtype: RoundManager
        """

        return RoundManager(
            players=self.players,
            player_teams=self.player_teams,
            trumps=self.trumps,
            card_power_calculator=self.card_power_calculator,
            card_decision_validator=self.card_decision_validator,
            active_team=self.active_team,
            game_renderer=self.game_renderer,
        )

    def create_winners_selector(self) -> WinnersSelector:
        """
        Creates a winners selector object.
        :return: A winners selector object
        :rtype: WinnersSelector
        """

        return WinnersSelector(teams=self.teams, active_team=self.active_team)

    @abstractmethod
    def create_money_distributer(self, winners: list[Player]) -> MoneyDistributer:
        """
        Creates a money distributer object.
        :return: A money distributer object
        :rtype: MoneyDistributer
        """
        pass

    def sort_player_hands(self) -> None:
        """
        Sorts the cards of the players according to their power in the game.
        :return: None
        """

        for player in self.players:
            player.player_cards.sort(
                key=self.card_power_calculator.get_card_power, reverse=True
            )

    def calculate_runners_amount(self) -> None:
        """
        Creates a RunnersCalculator object, calculates the amount of
        game runners and sets the runners_amount variable of Game.
        :rtype: None
        """
        runners_calculator: RunnersCalculator = self.runners_calculator(self.trumps)
        runners_setup: RunnersSetup = runners_calculator.count_game_runners(
            teams=self.teams
        )
        self.runners_amount: int = runners_setup.runners_amount

    def handle_winners(self):
        """
        Creates an object that selects the winners.
        Creates another object after to distribute the money among the players.
        :return: None
        """

        winners_selector: WinnersSelector = self.create_winners_selector()
        winners: list[Player] = winners_selector.get_game_winners()
        most_point_teams: list[Team] = winners_selector.get_most_points_teams()
        self.game_renderer.render_most_point_teams(most_point_teams=most_point_teams)
        for team in most_point_teams:
            self.game_renderer.render_team_points(team=team)
            self.game_renderer.render_team_players(team=team)
        self.game_renderer.render_winners(winners=winners)
        money_distributer: MoneyDistributer = self.create_money_distributer(
            winners=winners
        )
        game_value: int = money_distributer.calculate_game_value()
        money_distributer.distribute_money(game_value=game_value, winners=winners)
        self.game_renderer.render_game_value_calculation(
            money_distributer=money_distributer, game_value=game_value
        )
        for player in self.players:
            self.game_renderer.render_player_money(player=player)

    def play_game(self) -> None:
        """
        Simulates a full game.
        :return: None
        """

        self.sort_player_hands()
        self.create_teams()
        self.calculate_runners_amount()
        self.round_manager: RoundManager = self.create_round_manager()
        assert self.round_manager is not None
        for i in range(len(self.players[0].player_cards)):
            self.round_manager.play_round(is_first_round=(i == 0))
        self.amount_game_value_doubles += self.round_manager.amt_game_val_doubles
        self.active_team: Team = self.round_manager.active_team
        self.handle_winners()
