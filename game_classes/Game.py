from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from system.custom_exceptions import PlayerHasNoTeamError
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

    name = "Game"
    game_mapping: dict[int, type[Game]] = {}
    is_choosable = False

    def __init_subclass__(cls):
        super().__init_subclass__()
        Game.game_mapping[len(Game.game_mapping) + 1] = cls

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
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
        self.renderer: Renderer = renderer
        self.card_power_calculator: CardPowerCalculator = card_power_calculator
        self.card_decision_validator: CardDecisionValidator = card_decision_validator
        self.amount_game_value_doubles: int = amount_game_value_doubles
        self.players: list[Player] = players
        self.total_card_points: int = sum(
            card.card_type.points for card in cards.full_deck
        )
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

    def create_solo_teams(self, game_chooser) -> None:
        team_1 = Team(team_name="Team 1")
        team_1.players.append(game_chooser)
        self.active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

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
        raise PlayerHasNoTeamError(f"{player} has no team!")

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

    def create_winners_selector(self) -> WinnersSelector:
        """
        Creates a winners selector object.
        :return: A winners selector object
        :rtype: WinnersSelector
        """

        return WinnersSelector(teams=self.teams, active_team=self.active_team)

    @abstractmethod
    def create_money_distributer(
        self, winners_selector: WinnersSelector
    ) -> MoneyDistributer:
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

    def play_round(self, rounds: int) -> None:
        """
        Simulates one round. Every player gets to play a card.
        The player who plays the strongest card is the round winner
        and starts the next round.
        :param rounds: The number of the current round (first round must be 1)
        :type rounds: int
        :return: None
        """

        shooting_possible: bool = False

        if rounds == 1:
            shooting_possible: bool = True

        for player in self.players:

            players_team: Team = self.get_players_team(player)

            if (
                shooting_possible
                and self.active_team is not None
                and players_team != self.active_team
            ):
                if player.is_shoots():
                    self.amount_game_value_doubles += 1
                    for prev_active_player in self.active_team.players:
                        if prev_active_player.is_shoots_back():
                            self.amount_game_value_doubles += 1
                            break
                    else:
                        self.active_team = players_team
                    shooting_possible = False

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
        round_winner_index = self.played_cards.index(strongest_card)
        for card in self.played_cards:
            self.players[round_winner_index].collected_cards.append(card)
        self.renderer.render(
            message=show_collector_of_cards(
                player_name=self.players[round_winner_index].player_name,
                collected_cards=self.players[round_winner_index].collected_cards,
            )
        )
        starter = self.players[round_winner_index]
        self.sort_players(starter=starter)
        self.played_cards.clear()

    def handle_winners(self):
        """
        Creates an object that selects the winners.
        Creates another object after to distribute the money among the players.
        :return: None
        """

        winners_selector: WinnersSelector = self.create_winners_selector()
        winners = winners_selector.get_game_winners()
        most_point_teams = winners_selector.get_most_points_teams()
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
        money_distributer: MoneyDistributer = self.create_money_distributer(
            winners_selector=winners_selector
        )
        game_value = money_distributer.calculate_game_value()
        money_distributer.distribute_money(game_value=game_value, winners=winners)
        self.renderer.render(message=tell_winners(winners=winners))
        for player in self.players:
            self.renderer.render(
                message=tell_player_money(
                    player_name=player.player_name, money=player.money
                )
            )

    def play_game(self) -> None:
        """
        Simulates a full game.
        :return: None
        """

        self.sort_player_hands()
        self.create_teams()
        self.runners_amount = self.count_game_runners(trumps=self.trumps)
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round(rounds=rounds + 1)
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
            card_power_calculator=RamschCardPowerCalculator(),
            players=players,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=RamschCardDecisionValidator(),
        )
        self.alone_price = alone_price
        self.trump_color = Color.HERZ
        self.trump_types = [Type.OBER, Type.UNTER]
        self.trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in self.trump_types or card.card_color == self.trump_color
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        self.active_players: list[Player] = []

    def create_teams(self) -> None:
        for index in range(len(self.players)):
            team = Team(team_name=f"Team {index + 1}")
            team.players.append(self.players[index])
            self.teams.append(team)

    def create_winners_selector(self) -> WinnersSelector:
        return RamschWinnersSelector(
            teams=self.teams, active_players=self.active_players
        )

    def play_round(self, rounds: int) -> None:
        if rounds == 1:
            for player in self.players:
                if player.is_shoots():
                    self.amount_game_value_doubles += 1
                    self.active_players.append(player)
        super().play_round(rounds=rounds)

    def create_money_distributer(
        self, winners_selector: WinnersSelector
    ) -> MoneyDistributer:
        money_distributer: MoneyDistributer = RamschMoneyDistributer(
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            winners=winners_selector.get_game_winners(),
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
            card_power_calculator=SauspielCardPowerCalculator(),
            players=players,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=SauspielCardDecisionValidator(
                call_sau=Card(card_color=sau_color, card_type=Type.SAU)
            ),
        )
        self.game_chooser = game_chooser
        self.base_price = base_price
        self.call_price = call_price
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
            if any(card == self.call_sau for card in player.player_cards):
                team_1.players.append(player)
                break
        self.active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

    def create_money_distributer(
        self, winners_selector: WinnersSelector
    ) -> MoneyDistributer:
        assert self.active_team is not None
        money_distributer = SauspielMoneyDistributer(
            base_price=self.base_price,
            call_price=self.call_price,
            players=self.players,
            teams=self.teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners_selector.get_game_winners(),
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
            card_power_calculator=WenzCardPowerCalculator(),
            players=players,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=WenzCardDecisionValidator(),
        )
        self.game_chooser = game_chooser
        self.trump_types = [Type.UNTER]
        self.trumps: list[Card] = [
            card for card in self.cards.full_deck if card.card_type in self.trump_types
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        self.alone_price = alone_price
        self.base_price = base_price
        self.minimum_runners: int = 2

    def create_teams(self) -> None:
        self.create_solo_teams(game_chooser=self.game_chooser)

    def create_money_distributer(
        self, winners_selector: WinnersSelector
    ) -> MoneyDistributer:
        assert self.active_team is not None
        money_distributer = WenzMoneyDistributer(
            base_price=self.base_price,
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners_selector.get_game_winners(),
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
            card_power_calculator=SoloCardPowerCalculator(trump_color=trump_color),
            players=players,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=SoloCardDecisionValidator(),
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
        self.minimum_runners: int = 3

    def create_teams(self) -> None:
        self.create_solo_teams(game_chooser=self.game_chooser)

    def create_money_distributer(
        self, winners_selector: WinnersSelector
    ) -> MoneyDistributer:
        assert self.active_team is not None
        money_distributer = SoloMoneyDistributer(
            base_price=self.base_price,
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners_selector.get_game_winners(),
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
        return money_distributer
