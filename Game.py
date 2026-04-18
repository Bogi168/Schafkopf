from abc import ABC, abstractmethod

from Cards import Cards, Card, Type, Color
from Player import Player, Team
from Renderer import Renderer

from CardPowerCalculator import (
    CardPowerCalculator,
    RamschCardPowerCalculator,
    SauspielCardPowerCalculator,
    WenzCardPowerCalculator,
    SoloCardPowerCalculator,
)
from CardDecisionValidator import (
    CardDecisionValidator,
    RamschCardDecisionValidator,
    SauspielCardDecisionValidator,
    WenzCardDecisionValidator,
    SoloCardDecisionValidator,
)

from MoneyDistributer import (
    MoneyDistributer,
    RamschMoneyDistributer,
    SauspielMoneyDistributer,
    WenzMoneyDistributer,
    SoloMoneyDistributer,
)

from text import (
    show_played_cards,
    show_collector_of_cards,
    tell_winners,
    tell_player_money,
)


class Game(ABC):
    rank = 0

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        players: list[Player],
        game_chooser: Player | None,
    ) -> None:
        self.cards: Cards = cards
        self.renderer: Renderer = renderer
        self.card_power_calculator: CardPowerCalculator = card_power_calculator
        self.card_decision_validator: CardDecisionValidator = card_decision_validator
        self.money_distributer: MoneyDistributer | None = None
        self.players: list[Player] = players
        self.game_chooser: Player | None = game_chooser
        self.trump_types: list[Type] = []
        self.teams: list[Team] = []
        self.played_cards: list[Card] = []
        self.trumps: list[Card] = []

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

    @abstractmethod
    def create_money_distributer(self) -> MoneyDistributer:
        pass

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
        winners = self.money_distributer.identify_game_winners()
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
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round()
        self.handle_winners()


class Ramsch(Game):
    rank = 1

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player | None,
        alone_price: int,
        amount_game_value_doublers: int,
    ) -> None:
        super().__init__(
            cards=cards,
            renderer=renderer,
            card_power_calculator=RamschCardPowerCalculator(),
            card_decision_validator=RamschCardDecisionValidator(),
            players=players,
            game_chooser=game_chooser,
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

    def create_money_distributer(self) -> MoneyDistributer:
        money_distributer = RamschMoneyDistributer(
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            renderer=self.renderer,
            amount_game_value_doublers=self.amount_game_value_doublers,
        )
        return money_distributer

    def play_game(self) -> None:
        self.sort_player_hands()
        self.create_teams()
        self.money_distributer: MoneyDistributer = self.create_money_distributer()
        super().play_game()


class Sauspiel(Game):
    rank = 2

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        sau_color: Color,
        game_chooser: Player | None,
        base_price: int,
        call_price: int,
        amount_game_value_doublers: int,
    ) -> None:
        super().__init__(
            cards=cards,
            renderer=renderer,
            card_power_calculator=SauspielCardPowerCalculator(),
            card_decision_validator=SauspielCardDecisionValidator(
                call_sau=[
                    card
                    for card in cards.full_deck
                    if card.card_color == sau_color and card.card_type == Type.SAU
                ][0]
            ),
            players=players,
            game_chooser=game_chooser,
        )
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
        self.sau_color = sau_color
        self.active_team: Team | None = None

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
        self.active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        self.teams.append(team_1)
        self.teams.append(team_2)

    def create_money_distributer(self) -> MoneyDistributer:
        money_distributer = SauspielMoneyDistributer(
            base_price=self.base_price,
            call_price=self.call_price,
            players=self.players,
            teams=self.teams,
            renderer=self.renderer,
            amount_game_value_doublers=self.amount_game_value_doublers,
            active_team=self.active_team,
        )
        return money_distributer

    def play_game(self) -> None:
        self.sort_player_hands()
        self.create_teams()
        self.money_distributer = self.create_money_distributer()
        self.money_distributer.count_game_runners(trumps=self.trumps)
        super().play_game()


class Wenz(Game):
    rank = 4

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player | None,
        base_price: int,
        alone_price: int,
        amount_game_value_doublers: int,
    ) -> None:
        super().__init__(
            cards=cards,
            renderer=renderer,
            card_power_calculator=WenzCardPowerCalculator(),
            card_decision_validator=WenzCardDecisionValidator(),
            players=players,
            game_chooser=game_chooser,
        )
        self.trump_types = [Type.UNTER]
        self.trumps: list[Card] = [
            card for card in self.cards.full_deck if card.card_type in self.trump_types
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        self.active_team: Team | None = None
        self.alone_price = alone_price
        self.base_price = base_price
        self.amount_game_value_doublers = amount_game_value_doublers

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

    def create_money_distributer(self) -> MoneyDistributer:
        money_distributer = WenzMoneyDistributer(
            base_price=self.base_price,
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            renderer=self.renderer,
            amount_game_value_doublers=self.amount_game_value_doublers,
            active_team=self.active_team,
        )
        return money_distributer

    def play_game(self) -> None:
        self.sort_player_hands()
        self.create_teams()
        self.money_distributer = self.create_money_distributer()
        self.money_distributer.count_game_runners(trumps=self.trumps)
        super().play_game()


class Solo(Game):
    rank = 6

    def __init__(
        self,
        trump_color: Color,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player | None,
        base_price: int,
        alone_price: int,
        amount_game_value_doublers: int,
    ) -> None:
        super().__init__(
            cards=cards,
            renderer=renderer,
            card_power_calculator=SoloCardPowerCalculator(trump_color=trump_color),
            card_decision_validator=SoloCardDecisionValidator(),
            players=players,
            game_chooser=game_chooser,
        )
        self.trump_color: Color = trump_color
        self.trump_types = [Type.OBER, Type.UNTER]
        self.trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in self.trump_types or card.card_color == self.trump_color
        ]
        self.trumps.sort(key=self.card_power_calculator.get_card_power, reverse=True)
        self.active_team: Team | None = None
        self.alone_price = alone_price
        self.base_price = base_price
        self.amount_game_value_doublers = amount_game_value_doublers

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

    def create_money_distributer(self) -> MoneyDistributer:
        money_distributer = SoloMoneyDistributer(
            base_price=self.base_price,
            alone_price=self.alone_price,
            players=self.players,
            teams=self.teams,
            renderer=self.renderer,
            amount_game_value_doublers=self.amount_game_value_doublers,
            active_team=self.active_team,
        )
        return money_distributer

    def play_game(self) -> None:
        self.sort_player_hands()
        self.create_teams()
        self.money_distributer = self.create_money_distributer()
        self.money_distributer.count_game_runners(trumps=self.trumps)
        super().play_game()
