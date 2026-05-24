from __future__ import annotations
from typing import TYPE_CHECKING

from card_classes.CardPowerCalculator import SoloCardPowerCalculator
from game_classes.Game import Game
from card_classes.Cards import Color, Type
from input_validators.CardDecisionValidator import SoloCardDecisionValidator
from money_handling.MoneyDistributer import SoloMoneyDistributer
from player_classes.TeamBuilder import SoloTeamBuilder
from game_classes.RunnersCalculator import RunnersCalculator
from game_classes.game_modes.GameRegistry import GameRegistry

if TYPE_CHECKING:
    from player_classes.Player import Player
    from system.Renderer import Renderer
    from card_classes.Cards import Cards
    from money_handling.MoneyDistributer import MoneyDistributer


@GameRegistry.register_game
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
            runners_calculator=RunnersCalculator,
            card_power_calculator=SoloCardPowerCalculator(trump_color=trump_color),
            players=players,
            trump_types=[Type.OBER, Type.UNTER],
            trump_color=trump_color,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=SoloCardDecisionValidator(),
        )
        self.game_chooser: Player = game_chooser
        self.alone_price: int = alone_price
        self.base_price: int = base_price

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
