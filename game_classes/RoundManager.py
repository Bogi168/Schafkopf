from __future__ import annotations
from typing import TYPE_CHECKING

from player_classes.Team import Team

if TYPE_CHECKING:
    from player_classes.Player import Player
    from card_classes.Cards import Card
    from card_classes.CardPowerCalculator import CardPowerCalculator
    from input_validators.CardDecisionValidator import CardDecisionValidator
    from game_classes.GameRenderer import GameRenderer


class RoundManager:
    def __init__(
        self,
        players: list[Player],
        player_teams: dict[Player, Team],
        trumps: list[Card],
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        active_team: Team | None,
        game_renderer: GameRenderer,
    ) -> None:
        self.players: list[Player] = players
        self.player_teams: dict[Player, Team] = player_teams
        self.trumps: list[Card] = trumps
        self.active_team: Team | None = active_team
        self.card_power_calculator: CardPowerCalculator = card_power_calculator
        self.card_decision_validator: CardDecisionValidator = card_decision_validator
        self.game_renderer: GameRenderer = game_renderer
        self.played_cards: list[Card] = []
        self.amt_round_game_val_doubles: int = 0

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

    def play_round(self, is_first_round: bool) -> None:
        """
        Simulates one round. Every player gets to play a card.
        The player who plays the strongest card is the round winner
        and starts the next round.
        :param is_first_round: A boolean indicating whether it is the first round of the game
        :type is_first_round: bool
        :return: None
        """

        if is_first_round:
            shooting_possible: bool = True
        else:
            shooting_possible: bool = False

        for player in self.players:

            players_team: Team = self.player_teams[player]

            if (
                shooting_possible
                and isinstance(self.active_team, Team)
                and players_team != self.active_team
            ):
                if player.ask_shoot():
                    self.amt_round_game_val_doubles += 1
                    for prev_active_player in self.active_team.players:
                        if prev_active_player.ask_shoot(ask_shoot_back=True):
                            self.amt_round_game_val_doubles += 1
                            break
                    else:
                        self.active_team = players_team
                    shooting_possible = False

            card_decision: Card = player.get_card_decision(
                move_validator=lambda d, p=player: self.card_decision_validator.is_move_legal(
                    player_cards=p.player_cards,
                    decision=d,
                    trumps=self.trumps,
                    lead_card=self.lead_card,
                ),
            )

            self.played_cards.append(card_decision)

            self.game_renderer.render_played_cards(played_cards=self.played_cards)
        strongest_card: Card = self.card_power_calculator.get_strongest_played_card(
            played_cards=self.played_cards, trumps=self.trumps
        )
        round_winner_index: int = self.played_cards.index(strongest_card)
        for card in self.played_cards:
            self.players[round_winner_index].collected_cards.append(card)
        self.game_renderer.render_collector_of_cards(
            collector=self.players[round_winner_index]
        )
        starter: Player = self.players[round_winner_index]
        self.sort_players(starter=starter)
        self.played_cards.clear()


class RamschRoundManager(RoundManager):

    def __init__(
        self,
        players: list[Player],
        player_teams: dict[Player, Team],
        trumps: list[Card],
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        game_renderer: GameRenderer,
    ) -> None:
        super().__init__(
            players=players,
            player_teams=player_teams,
            trumps=trumps,
            card_power_calculator=card_power_calculator,
            card_decision_validator=card_decision_validator,
            active_team=None,
            game_renderer=game_renderer,
        )
        self.active_players: list[Player] = []

    def play_round(self, rounds: int) -> None:
        if rounds == 1:
            for player in self.players:
                if player.ask_shoot():
                    self.amt_round_game_val_doubles += 1
                    self.active_players.append(player)
        super().play_round(rounds=rounds)
