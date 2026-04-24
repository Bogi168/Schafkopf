from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from money_handling.WinnersSelector import WinnersSelector, RamschWinnersSelector
from player_classes.Team import Team
from card_classes.Cards import Card, Type, Color
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

from system.text import (
    show_played_cards,
    show_collector_of_cards,
    tell_most_point_teams,
    tell_team_points,
    tell_team_players,
    tell_winners,
    tell_player_money,
)

if TYPE_CHECKING:
    from player_classes.Player import Player
    from system.Renderer import Renderer
    from card_classes.Cards import Cards


class Game(ABC):
    """An object that represents the game"""

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        card_power_calculator: CardPowerCalculator,
        players: list[Player],
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
        """

        self.cards: Cards = cards
        self.renderer: Renderer = renderer
        self.card_power_calculator: CardPowerCalculator = card_power_calculator
        self.card_decision_validator: CardDecisionValidator | None = None
        self.money_distributer: MoneyDistributer | None = None
        self.winners_selector: WinnersSelector | None = None
        self.players: list[Player] = players
        self.teams: list[Team] = []
        self.played_cards: list[Card] = []
        self.trumps: list[Card] = []
        self.active_team: Team | None = None
        self.minimum_runners: int = 0
        self.runners_amount: int = 0

    @property
    def lead_card(self) -> Card | None:
        """
        :return: The first played card of the round
        :rtype: Card | None
        """

        if self.played_cards:
            return self.played_cards[0]
        else:
            return None

    @abstractmethod
    def create_teams(self) -> None:
        """Creates the team objects"""

        pass

    def sort_players(self, starter: Player) -> None:
        """
        Sorts the list of Players.
        The given starter moves to Index 0, but the order remains the same.
        :param starter: The player who should start the next game or round
        :type starter: Player
        :return: None
        """

        starter_index = self.players.index(starter)
        self.players = self.players[starter_index:] + self.players[:starter_index]

    @abstractmethod
    def create_card_decision_validator(self) -> CardDecisionValidator:
        """
        Creates a card decision validator object.
        :return: A card decision validator object
        :rtype: CardDecisionValidator
        """

        pass

    def create_winners_selector(self) -> WinnersSelector:
        """
        Creates a winners selector object.
        :return: A winners selector object
        :rtype: WinnersSelector
        """

        return WinnersSelector(teams=self.teams, active_team=self.active_team)

    @abstractmethod
    def create_money_distributer(self) -> MoneyDistributer:
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

        runners_count = 0
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

    def play_round(self) -> None:
        for player in self.players:
            assert self.card_decision_validator is not None
            player.card_decision(
                played_cards=self.played_cards,
                move_validator=lambda d, p=player: self.card_decision_validator.is_move_legal(
                    player=p, decision=d, trumps=self.trumps, lead_card=self.lead_card
                ),
            )
            self.renderer.render(
                message=show_played_cards(played_cards=self.played_cards)
            )
        strongest_card = self.card_power_calculator.get_strongest_played_card(
            played_cards=self.played_cards, trumps=self.trumps
        )
        winner_index = self.played_cards.index(strongest_card)
        for card in self.played_cards:
            self.players[winner_index].collected_cards.append(card)
        self.renderer.render(
            message=show_collector_of_cards(
                player_name=self.players[winner_index].player_name,
                collected_cards=self.players[winner_index].collected_cards,
            )
        )
        starter = self.players[winner_index]
        self.sort_players(starter=starter)
        self.played_cards.clear()

    def handle_winners(self):
        self.winners_selector: WinnersSelector = self.create_winners_selector()
        assert self.winners_selector is not None
        winners = self.winners_selector.get_game_winners()
        most_point_teams = self.winners_selector.get_most_points_teams()
        self.renderer.render(
            message=tell_most_point_teams(most_point_teams=most_point_teams)
        )
        for team in most_point_teams:
            self.renderer.render(
                message=tell_team_points(team_name=team.team_name, points=team.points)
            )
            self.renderer.render(
                message=tell_team_players(
                    team_name=team.team_name, players=team.players
                )
            )
        self.money_distributer: MoneyDistributer = self.create_money_distributer()
        assert self.money_distributer is not None
        game_value = self.money_distributer.calculate_game_value()
        self.money_distributer.distribute_money(game_value=game_value, winners=winners)
        self.renderer.render(message=tell_winners(winners=winners))
        for player in self.players:
            self.renderer.render(
                message=tell_player_money(
                    player_name=player.player_name, money=player.money
                )
            )

    def play_game(self) -> None:
        self.sort_player_hands()
        self.create_teams()
        self.runners_amount = self.count_game_runners(trumps=self.trumps)
        self.card_decision_validator = self.create_card_decision_validator()
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round()
        self.handle_winners()


class Ramsch(Game):

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        alone_price: int,
        amount_game_value_doublers: int,
    ) -> None:
        super().__init__(
            cards=cards,
            renderer=renderer,
            card_power_calculator=RamschCardPowerCalculator(),
            players=players,
        )
        self.alone_price = alone_price
        self.amount_game_value_doublers = amount_game_value_doublers
        self.trump_color = Color.HERZ
        self.trump_types = [Type.OBER, Type.UNTER]
        self.trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in self.trump_types or card.card_color == self.trump_color
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)

    def create_teams(self) -> None:
        for index in range(len(self.players)):
            team = Team(team_name=f"Team {index + 1}")
            team.players.append(self.players[index])
            self.teams.append(team)

    def create_card_decision_validator(self) -> CardDecisionValidator:
        card_decision_validator = RamschCardDecisionValidator()
        return card_decision_validator

    def create_winners_selector(self) -> WinnersSelector:
        return RamschWinnersSelector(teams=self.teams)

    def create_money_distributer(self) -> MoneyDistributer:
        assert self.winners_selector is not None
        money_distributer: MoneyDistributer = RamschMoneyDistributer(
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            amount_game_value_doublers=self.amount_game_value_doublers,
            winners=self.winners_selector.get_game_winners(),
            amount_game_card_points=sum(
                card.card_type.points for card in self.cards.full_deck
            ),
        )
        return money_distributer


class Sauspiel(Game):

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        sau_color: Color,
        game_chooser: Player,
        base_price: int,
        call_price: int,
        amount_game_value_doublers: int,
    ) -> None:
        super().__init__(
            cards=cards,
            renderer=renderer,
            card_power_calculator=SauspielCardPowerCalculator(),
            players=players,
        )
        self.game_chooser = game_chooser
        self.base_price = base_price
        self.call_price = call_price
        self.amount_game_value_doublers = amount_game_value_doublers
        self.trump_color = Color.HERZ
        self.trump_types = [Type.OBER, Type.UNTER]
        self.trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in self.trump_types or card.card_color == self.trump_color
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        self.call_sau: Card = Card(card_color=sau_color, card_type=Type.SAU)
        self.minimum_runners: int = 3

    def create_teams(self) -> None:
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        for player in self.players:
            for card in player.player_cards:
                if card == self.call_sau:
                    team_1.players.append(player)
        self.active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

    def create_card_decision_validator(self) -> CardDecisionValidator:
        card_decision_validator = SauspielCardDecisionValidator(call_sau=self.call_sau)
        return card_decision_validator

    def create_money_distributer(self) -> MoneyDistributer:
        assert self.active_team is not None
        assert self.winners_selector is not None
        money_distributer = SauspielMoneyDistributer(
            base_price=self.base_price,
            call_price=self.call_price,
            players=self.players,
            teams=self.teams,
            amount_game_value_doublers=self.amount_game_value_doublers,
            active_team=self.active_team,
            winners=self.winners_selector.get_game_winners(),
            runners_amount=self.runners_amount,
            amount_game_card_points=sum(
                card.card_type.points for card in self.cards.full_deck
            ),
        )
        return money_distributer


class Wenz(Game):

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player,
        base_price: int,
        alone_price: int,
        amount_game_value_doublers: int,
    ) -> None:
        super().__init__(
            cards=cards,
            renderer=renderer,
            card_power_calculator=WenzCardPowerCalculator(),
            players=players,
        )
        self.game_chooser = game_chooser
        self.trump_types = [Type.UNTER]
        self.trumps: list[Card] = [
            card for card in self.cards.full_deck if card.card_type in self.trump_types
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        self.alone_price = alone_price
        self.base_price = base_price
        self.amount_game_value_doublers = amount_game_value_doublers
        self.minimum_runners: int = 2

    def create_teams(self) -> None:
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        self.active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

    def create_card_decision_validator(self) -> CardDecisionValidator:
        card_decision_validator = WenzCardDecisionValidator()
        return card_decision_validator

    def create_money_distributer(self) -> MoneyDistributer:
        assert self.active_team is not None
        assert self.winners_selector is not None
        money_distributer = WenzMoneyDistributer(
            base_price=self.base_price,
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            amount_game_value_doublers=self.amount_game_value_doublers,
            active_team=self.active_team,
            winners=self.winners_selector.get_game_winners(),
            runners_amount=self.runners_amount,
            amount_game_card_points=sum(
                card.card_type.points for card in self.cards.full_deck
            ),
        )
        return money_distributer


class Solo(Game):

    def __init__(
        self,
        trump_color: Color,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player,
        base_price: int,
        alone_price: int,
        amount_game_value_doublers: int,
    ) -> None:
        super().__init__(
            cards=cards,
            renderer=renderer,
            card_power_calculator=SoloCardPowerCalculator(trump_color=trump_color),
            players=players,
        )
        self.game_chooser = game_chooser
        self.trump_color: Color = trump_color
        self.trump_types = [Type.OBER, Type.UNTER]
        self.trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in self.trump_types or card.card_color == self.trump_color
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        self.alone_price = alone_price
        self.base_price = base_price
        self.amount_game_value_doublers = amount_game_value_doublers
        self.minimum_runners: int = 3

    def create_teams(self) -> None:
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        self.active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

    def create_card_decision_validator(self) -> CardDecisionValidator:
        card_decision_validator = SoloCardDecisionValidator()
        return card_decision_validator

    def create_money_distributer(self) -> MoneyDistributer:
        assert self.active_team is not None
        assert self.winners_selector is not None
        money_distributer = SoloMoneyDistributer(
            base_price=self.base_price,
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            amount_game_value_doublers=self.amount_game_value_doublers,
            active_team=self.active_team,
            winners=self.winners_selector.get_game_winners(),
            runners_amount=self.runners_amount,
            amount_game_card_points=sum(
                card.card_type.points for card in self.cards.full_deck
            ),
        )
        return money_distributer
