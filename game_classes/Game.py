from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from game_classes.GameRenderer import GameRenderer
from game_classes.RoundManager import RoundManager, RamschRoundManager
from money_handling.WinnersSelector import WinnersSelector, RamschWinnersSelector
from player_classes.Team import Team
from card_classes.Cards import Card, Type, Color
from player_classes.TeamBuilder import (
    RamschTeamBuilder,
    SauspielTeamBuilder,
    WenzTeamBuilder,
    SoloTeamBuilder,
)
from card_classes.CardPowerCalculator import (
    CardPowerCalculator,
    RamschCardPowerCalculator,
    SauspielCardPowerCalculator,
    WenzCardPowerCalculator,
    SoloCardPowerCalculator,
)
from input_validators.CardDecisionValidator import (
    CardDecisionValidator,
    RamschCardDecisionValidator,
    SauspielCardDecisionValidator,
    WenzCardDecisionValidator,
    SoloCardDecisionValidator,
)

from money_handling.MoneyDistributer import (
    MoneyDistributer,
    RamschMoneyDistributer,
    SauspielMoneyDistributer,
    WenzMoneyDistributer,
    SoloMoneyDistributer,
)

if TYPE_CHECKING:
    from player_classes.Player import Player
    from system.Renderer import Renderer
    from card_classes.Cards import Cards
    from player_classes.TeamBuilder import TeamSetup, TeamBuilder


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
        self.game_renderer: GameRenderer = GameRenderer(renderer=renderer)
        self.amount_game_value_doubles: int = amount_game_value_doubles
        self.players: list[Player] = players
        self.round_manager: RoundManager | None = None
        self.total_card_points: int = sum(
            card.card_type.points for card in cards.full_deck
        )
        self.player_teams: dict[Player, Team] = dict()
        self.teams: list[Team] = []
        self.trump_types: list[Type] | None = None
        self.trump_color: Color | None = None
        self.trumps: list[Card] = []
        self.active_team: Team | None = None
        self.minimum_runners: int = 0
        self.runners_amount: int = 0

    def set_trumps(self) -> list[Card]:
        """
        Creates a list of all trump cards of the game
        :return: The list of trump cards
        :rtype: list[Card]
        """

        assert self.trump_types is not None
        trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in self.trump_types or card.card_color == self.trump_color
        ]
        trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        return trumps

    def create_teams(self) -> None:
        """Creates the team objects and adds them to the teams list."""
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

    @staticmethod
    def count_team_runners(team: Team, trumps: list[Card]) -> int:
        """
        Counts the amount of runners a team has.
        :param team: The team object
        :type team: Team
        :param trumps: A list of all the trump cards
        :type trumps: list[Card]
        :return: The amount of runners the given team has
        :rtype: int
        """

        runners_count: int = 0
        for trump in trumps:
            if any(
                card == trump for player in team.players for card in player.player_cards
            ):
                runners_count += 1
            else:
                return runners_count
        return runners_count

    def count_game_runners(self, trumps: list[Card]) -> int:
        """
        Counts the amount of runners for each team and returns the game runners count.
        :param trumps: A list of all the trump cards
        :type trumps: list[Card]
        :return: The amount of runners the game has
        :rtype: int
        """

        for team in self.teams:
            runners_count: int = self.count_team_runners(team=team, trumps=trumps)
            if runners_count >= self.minimum_runners:
                return runners_count
        return 0

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

        self.trumps: list[Card] = self.set_trumps()
        self.sort_player_hands()
        self.create_teams()
        self.runners_amount: int = self.count_game_runners(trumps=self.trumps)
        self.round_manager: RoundManager = self.create_round_manager()
        assert self.round_manager is not None
        for i in range(len(self.players[0].player_cards)):
            self.round_manager.play_round(is_first_round=(i == 0))
        self.amount_game_value_doubles += self.round_manager.amt_game_val_doubles
        self.active_team: Team = self.round_manager.active_team
        self.handle_winners()


class Ramsch(Game):
    """
    The trump types are Ober and Unter.
    The trump color is Herz
    There are no real teams, everybody plays alone.
    The goal is to earn the least amount of points during the game.
    The player with the most points loses the game.
    If multiple players have the same amount of points, all of them lose,
    expect one or more of them shot (doubled the game value and turned active).
    If the player with the most points has 91 points or more, he is the winner of the game.
    """

    name = "Ramsch"
    rank = 1
    is_choosable = False

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        alone_price: int,
        amount_game_value_doubles: int,
    ) -> None:
        """
        :param cards: An object which saves a full deck of cards and provides a deck to play with
        :type cards: Cards
        :param renderer: An object which renders information
        :type renderer: Renderer
        :param players: A list of objects which represent the players
        :type players: list[Player]
        :param alone_price: alone price for game value calculations
        :type alone_price: int
        :param amount_game_value_doubles: The amount of people who decided to double the game value
        :type amount_game_value_doubles: int
        """

        super().__init__(
            cards=cards,
            renderer=renderer,
            team_builder=RamschTeamBuilder(players=players),
            card_power_calculator=RamschCardPowerCalculator(),
            players=players,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=RamschCardDecisionValidator(),
        )
        self.alone_price: int = alone_price
        self.trump_color: Color = Color.HERZ
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]
        self.active_players: list[Player] = []

    def create_round_manager(self) -> RoundManager:
        return RamschRoundManager(
            players=self.players,
            player_teams=self.player_teams,
            trumps=self.trumps,
            card_power_calculator=self.card_power_calculator,
            card_decision_validator=self.card_decision_validator,
            game_renderer=self.game_renderer,
        )

    def create_winners_selector(self) -> WinnersSelector:
        assert isinstance(self.round_manager, RamschRoundManager)
        self.active_players: list[Player] = self.round_manager.active_players
        return RamschWinnersSelector(
            teams=self.teams, active_players=self.active_players
        )

    def create_money_distributer(self, winners: list[Player]) -> MoneyDistributer:
        money_distributer: MoneyDistributer = RamschMoneyDistributer(
            alone_price=self.alone_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            winners=winners,
            amount_game_card_points=self.total_card_points,
        )
        return money_distributer


class Sauspiel(Game):
    """
    The trump types are Ober and Unter.
    The trump color is Herz
    Choosing Sauspiel is only possible if you have cards that are not trumps
    and don't have the Sau for every non-trump card color you have.
    The player who chooses the game has to choose a sau color.
    The sau color decision is only legal, if he/she doesn't own the sau of the chosen sau color
    and has at least one non-trump card of the chosen sau color.
    The game chooser and the person who owns the sau of the chosen sau color (the so called callsau) build a team.
    Until the callsau is played, nobody knows for sure, who his teammates are.
    If the first played card of a round is from the color of the callsau, the owner of the callsau has to play it.
    There are no other scenarios in which the callsau is allowed to be played,
    apart from it being the last card the player has.
    The goal is to earn the highest amount of points as a team during the game.
    The team with the most points wins the game.
    If multiple teams have the same amount of points, the team that didn't choose the game wins,
    except somebody from the other team shot and the team of the game chooser didn't shoot back
    (doubled the game value and turned active).
    """

    name = "Sauspiel"
    rank = 2
    is_choosable = True

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        sau_color: Color,
        game_chooser: Player,
        base_price: int,
        call_price: int,
        amount_game_value_doubles: int,
    ) -> None:
        """
        :param cards: An object which saves a full deck of cards and provides a deck to play with
        :type cards: Cards
        :param renderer: An object which renders information
        :type renderer: Renderer
        :param players: A list of objects which represent the players
        :type players: list[Player]
        :param sau_color: The color of the callsau
        :type sau_color: Color
        :param game_chooser: The player who choose the game
        :type game_chooser: Player
        :param base_price: base price for game value calculations
        :type base_price: int
        :param call_price: call price for game value calculations
        :type call_price: int
        :param amount_game_value_doubles: The amount of people who decided to double the game value
        :type amount_game_value_doubles: int
        """

        super().__init__(
            cards=cards,
            renderer=renderer,
            team_builder=SauspielTeamBuilder(
                players=players,
                call_sau=Card(card_color=sau_color, card_type=Type.SAU),
                game_chooser=game_chooser,
            ),
            card_power_calculator=SauspielCardPowerCalculator(),
            players=players,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=SauspielCardDecisionValidator(
                call_sau=Card(card_color=sau_color, card_type=Type.SAU)
            ),
        )
        self.game_chooser: Player = game_chooser
        self.base_price: int = base_price
        self.call_price: int = call_price
        self.trump_color: Color = Color.HERZ
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]
        self.call_sau: Card = Card(card_color=sau_color, card_type=Type.SAU)
        self.minimum_runners: int = 3

    def create_money_distributer(self, winners: list[Player]) -> MoneyDistributer:
        assert self.active_team is not None
        money_distributer: MoneyDistributer = SauspielMoneyDistributer(
            base_price=self.base_price,
            call_price=self.call_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners,
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
        return money_distributer


class Wenz(Game):
    """
    The only trump type is Unter.
    There are no trump colors.
    The game chooser has to play alone.
    The rest of the players build a team.
    The goal is to earn the highest amount of points as a team during the game.
    The team with the most points wins the game.
    If the game chooser and the rest have the same amount of points, the game chooser loses,
    except somebody from the other team shot and game chooser didn't shoot back
    (doubled the game value and turned active).
    """

    name = "Wenz"
    rank = 3
    is_choosable = True

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player,
        base_price: int,
        alone_price: int,
        amount_game_value_doubles: int,
    ) -> None:
        """
        :param cards: An object which saves a full deck of cards and provides a deck to play with
        :type cards: Cards
        :param renderer: An object which renders information
        :type renderer: Renderer
        :param players: A list of objects which represent the players
        :type players: list[Player]
        :param game_chooser: The player who choose the game
        :type game_chooser: Player
        :param base_price: base price for game value calculations
        :type base_price: int
        :param alone_price: alone price for game value calculations
        :type alone_price: int
        :param amount_game_value_doubles: The amount of people who decided to double the game value
        :type amount_game_value_doubles: int
        """

        super().__init__(
            cards=cards,
            renderer=renderer,
            team_builder=WenzTeamBuilder(players=players, game_chooser=game_chooser),
            card_power_calculator=WenzCardPowerCalculator(),
            players=players,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=WenzCardDecisionValidator(),
        )
        self.game_chooser: Player = game_chooser
        self.trump_types: list[Type] = [Type.UNTER]
        self.alone_price: int = alone_price
        self.base_price: int = base_price
        self.minimum_runners: int = 2

    def create_money_distributer(self, winners: list[Player]) -> MoneyDistributer:
        assert self.active_team is not None
        money_distributer: MoneyDistributer = WenzMoneyDistributer(
            base_price=self.base_price,
            alone_price=self.alone_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners,
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
        return money_distributer


class Solo(Game):
    """
    The trump types are Ober and Unter.
    The player who chooses the game has to choose a trump color.
    The trump color is the color chosen by the game chooser.
    The game chooser has to play alone.
    The rest of the players build a team.
    The goal is to earn the highest amount of points as a team during the game.
    The team with the most points wins the game.
    If the game chooser and the rest have the same amount of points, the game chooser loses,
    except somebody from the other team shot and game chooser didn't shoot back
    (doubled the game value and turned active).
    """

    name = "Solo"
    rank = 4
    is_choosable = True

    def __init__(
        self,
        trump_color: Color,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player,
        base_price: int,
        alone_price: int,
        amount_game_value_doubles: int,
    ) -> None:
        """
        :param trump_color: The trump color chosen by the game chooser
        :type trump_color: Color
        :param cards: An object which saves a full deck of cards and provides a deck to play with
        :type cards: Cards
        :param renderer: An object which renders information
        :type renderer: Renderer
        :param players: A list of objects which represent the players
        :type players: list[Player]
        :param game_chooser: The player who choose the game
        :type game_chooser: Player
        :param base_price: base price for game value calculations
        :type base_price: int
        :param alone_price: alone price for game value calculations
        :type alone_price: int
        :param amount_game_value_doubles: The amount of people who decided to double the game value
        :type amount_game_value_doubles: int
        """

        super().__init__(
            cards=cards,
            renderer=renderer,
            team_builder=SoloTeamBuilder(players=players, game_chooser=game_chooser),
            card_power_calculator=SoloCardPowerCalculator(trump_color=trump_color),
            players=players,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=SoloCardDecisionValidator(),
        )
        self.game_chooser: Player = game_chooser
        self.trump_color: Color = trump_color
        self.trump_types: list[Type] = [Type.OBER, Type.UNTER]
        self.alone_price: int = alone_price
        self.base_price: int = base_price
        self.minimum_runners: int = 3

    def create_money_distributer(self, winners: list[Player]) -> MoneyDistributer:
        assert self.active_team is not None
        money_distributer: MoneyDistributer = SoloMoneyDistributer(
            base_price=self.base_price,
            alone_price=self.alone_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners,
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
        return money_distributer
