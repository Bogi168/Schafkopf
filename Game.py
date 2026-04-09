from abc import ABC, abstractmethod
from Cards import Cards, Card, Type, Color
from Player import Player
from Renderer import Renderer
from Team import Team


class Game(ABC):
    rank = 0

    def __init__(
        self,
        trump_color: Color | None,
        trump_types: list[Type],
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player | None,
        base_price: int,
        call_price: int,
        alone_price: int,
        sau_color: Color | None = None,
    ) -> None:
        self.trump_color = trump_color
        self.trump_types = trump_types
        self.cards = cards
        self.renderer = renderer
        self.players = players
        self.game_chooser = game_chooser
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price
        self.sau_color = sau_color
        self.runners_amount = 0
        self.winners: list[Player] = []

        self.trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in trump_types
            or (trump_color is not None and card.card_color == trump_color)
        ]
        self.trumps.sort(key=self.get_card_power, reverse=True)
        self.played_cards: list[Card] = []

        self.team_1 = Team(team_name="Team 1")
        self.team_2 = Team(team_name="Team 2")
        self.team_3 = Team(team_name="Team 3")
        self.team_4 = Team(team_name="Team 4")
        self.teams: list[Team] = [self.team_1, self.team_2, self.team_3, self.team_4]

    @property
    def call_sau(self) -> Card | None:
        call_sau = None
        for player in self.players:
            for card in player.player_cards:
                if card.card_color == self.sau_color and card.card_type == Type.SAU:
                    call_sau = card
        return call_sau

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

    def get_card_power(self, card: Card) -> int:
        power = 0
        trump_type_power = 1000
        trump_color_power = 100
        eichel_power = 80
        gruen_power = 60
        herz_power = 40
        schellen_power = 20

        if (
            self.trump_color is not None
            and card.card_type not in self.trump_types
            and card.card_color == self.trump_color
        ):
            power = trump_color_power + card.card_type.value
            return power

        match card.card_color:
            case Color.EICHEL:
                power = eichel_power + card.card_type.value
            case Color.GRUEN:
                power = gruen_power + card.card_type.value
            case Color.HERZ:
                power = herz_power + card.card_type.value
            case Color.SCHELLEN:
                power = schellen_power + card.card_type.value

        for trump_type in self.trump_types:
            if card.card_type == trump_type:
                power += trump_type_power
                return power
            else:
                trump_type_power -= 100

        return power

    def sort_player_hands(self):
        for player in self.players:
            player.player_cards.sort(key=self.get_card_power, reverse=True)

    def is_lead_card_null(self) -> bool:
        return self.lead_card is None

    def is_player_owns_call_sau(self, player_cards: list[Card]) -> bool:
        for card in player_cards:
            if card == self.call_sau:
                return True
        return False

    def is_lead_card_is_trump(self) -> bool:
        return self.lead_card in self.trumps

    def is_player_has_lead_card_color_available(self, player_cards: list[Card]) -> bool:
        if self.is_lead_card_null():
            return False
        for card in player_cards:
            if self.lead_card.card_color == card.card_color and card not in self.trumps:
                return True
        return False

    def is_player_has_trump_available(self, player_cards: list[Card]) -> bool:
        for card in player_cards:
            if card in self.trumps:
                return True
        return False

    @staticmethod
    def is_decision_in_legal_cards(decision: Card, legal_cards: list[Card]) -> bool:
        return decision in legal_cards

    def count_similar_color_cards(self, player_cards: list[Card], color: Color) -> int:
        color_count = 0
        for card in player_cards:
            if card.card_color == color and card not in self.trumps:
                color_count += 1
        return color_count

    def is_move_legal(self, player: Player, decision: Card) -> bool:

        if len(player.player_cards) == 1:
            return True

        player_has_lead = self.is_lead_card_null()
        if player_has_lead:
            if (
                isinstance(self, Sauspiel)
                and self.call_sau is not None
                and self.is_player_owns_call_sau(player_cards=player.player_cards)
                and decision.card_color == self.call_sau.card_color
                and decision not in self.trumps
                and decision != self.call_sau
                and self.count_similar_color_cards(
                    player_cards=player.player_cards, color=self.call_sau.card_color
                )
                < 4
            ):
                return False
            else:
                return True

        if (
            isinstance(self, Sauspiel)
            and self.call_sau is not None
            and self.is_player_owns_call_sau(player_cards=player.player_cards)
            and self.lead_card is not None
            and self.lead_card.card_color != self.call_sau.card_color
            and decision == self.call_sau
        ):
            return False

        else:
            assert self.lead_card is not None
            bool_lead_trump = self.is_lead_card_is_trump()
            if bool_lead_trump:
                trump_avail = self.is_player_has_trump_available(
                    player_cards=player.player_cards
                )
                if trump_avail:
                    legal = self.is_decision_in_legal_cards(
                        decision=decision, legal_cards=self.trumps
                    )
                else:
                    legal = True
            else:
                sim_col_avail = self.is_player_has_lead_card_color_available(
                    player_cards=player.player_cards
                )
                if sim_col_avail:
                    legal_cards = [
                        sim_color
                        for sim_color in player.player_cards
                        if sim_color.card_color == self.lead_card.card_color
                        and sim_color not in self.trumps
                    ]
                    if (
                        isinstance(self, Sauspiel)
                        and self.call_sau is not None
                        and self.is_player_owns_call_sau(
                            player_cards=player.player_cards
                        )
                        and self.lead_card.card_color == self.call_sau.card_color
                    ):
                        legal_cards = [self.call_sau]
                    legal = self.is_decision_in_legal_cards(
                        decision=decision, legal_cards=legal_cards
                    )
                else:
                    legal = True
        return legal

    def compare_card_rank(self, first_card: Card, second_card: Card) -> Card:
        if self.get_card_power(card=first_card) > self.get_card_power(second_card):
            return first_card
        else:
            return second_card

    def find_strongest_card(self) -> Card:
        strongest_card = self.lead_card
        for played_card in self.played_cards:

            # played_card != Trump -> strongest_card == Trump -> strongest_card = strongest_card
            if played_card not in self.trumps and strongest_card in self.trumps:
                pass

            # played_card == Trump -> strongest_card != Trump -> strongest_card = played_card
            elif played_card in self.trumps and strongest_card not in self.trumps:
                strongest_card = played_card

            # played_card == Trump -> strongest_card == Trump -> compare ranks
            elif played_card in self.trumps and strongest_card in self.trumps:
                strongest_card = self.compare_card_rank(
                    first_card=strongest_card, second_card=played_card
                )

            # strongest_card + played_card != Trump -> played_card_color != lead_card_color -> strongest_card = strongest_card
            elif played_card.card_color != self.lead_card.card_color:
                pass

            # strongest_card + played_card != Trump -> played_card_color == lead_card_color -> compare ranks
            else:
                strongest_card = self.compare_card_rank(
                    first_card=strongest_card, second_card=played_card
                )

        return strongest_card

    def play_round(self) -> None:
        for player in self.players:
            player.card_decision(
                renderer=self.renderer,
                played_cards=self.played_cards,
                move_validator=lambda d, p=player: self.is_move_legal(
                    player=p, decision=d
                ),
            )
            print(f"The played cards are: {self.played_cards}")
        strongest_card = self.find_strongest_card()
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

    def identify_most_points_teams(self) -> list[Team]:
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
        most_point_teams = self.identify_most_points_teams()
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
                print(f"There are {runners_count} runners")
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
        self.team_1.players.append(self.game_chooser)
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
            players=players,
            game_chooser=game_chooser,
            base_price=base_price,
            call_price=call_price,
            alone_price=alone_price,
        )

    def create_teams(self) -> None:
        self.team_1.players.clear()
        for index in range(len(self.players)):
            self.teams[index].players.append(self.players[index])

    def identify_game_winners(self) -> list[Player]:
        winners: list[Player] = []
        most_point_teams = self.identify_most_points_teams()
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
            players=players,
            game_chooser=game_chooser,
            base_price=base_price,
            call_price=call_price,
            alone_price=alone_price,
            sau_color=sau_color,
        )

    def create_teams(self) -> None:
        self.teams.remove(self.team_3)
        self.teams.remove(self.team_4)
        for player in self.players:
            for card in player.player_cards:
                if card == self.call_sau:
                    self.team_1.players.append(player)
        self.team_2.players = [
            player for player in self.players if player not in self.team_1.players
        ]

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.call_price
        game_value += self.runners_amount * self.base_price
        winning_team = self.find_players_team(player=self.winners[0])
        if winning_team.points == 120:
            game_value += 2 * self.base_price
        elif winning_team.points > 90 or (
            winning_team.points == 90 and self.game_chooser not in winning_team.players
        ):
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
            players=players,
            game_chooser=game_chooser,
            base_price=base_price,
            call_price=call_price,
            alone_price=alone_price,
        )

    def create_teams(self) -> None:
        self.teams.remove(self.team_3)
        self.teams.remove(self.team_4)
        self.team_2.players = [
            player for player in self.players if player not in self.team_1.players
        ]

    def get_card_power(self, card: Card) -> int:
        power = super().get_card_power(card=card)
        if card.card_type == Type.OBER:
            power -= 5
        return power

    def count_game_runners(self, minimum_runners: int = 2) -> int:
        return super().count_game_runners(minimum_runners=minimum_runners)

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.alone_price
        game_value += self.runners_amount * self.base_price
        winning_team = self.find_players_team(player=self.winners[0])

        if winning_team.points == 120:
            game_value += 2 * self.base_price
        elif winning_team.points > 90 or (
            winning_team.points == 90 and self.game_chooser not in winning_team.players
        ):
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
            players=players,
            game_chooser=game_chooser,
            base_price=base_price,
            call_price=call_price,
            alone_price=alone_price,
        )

    def create_teams(self) -> None:
        self.teams.remove(self.team_3)
        self.teams.remove(self.team_4)
        self.team_2.players = [
            player for player in self.players if player not in self.team_1.players
        ]

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.alone_price
        game_value += self.runners_amount * self.base_price
        winning_team = self.find_players_team(player=self.winners[0])

        if winning_team.points == 120:
            game_value += 2 * self.base_price
        elif winning_team.points > 90 or (
            winning_team.points == 90 and self.game_chooser not in winning_team.players
        ):
            game_value += self.base_price
        return game_value
