from abc import ABC, abstractmethod
from Cards import Cards, Card, Type, Color
from Player import Player
from Renderer import Renderer
from Team import Team
from handle_cards import find_strongest_card
from rulebook import (
    check_lead_card,
    check_player_owns_call_sau,
    check_lead_card_trump,
    similar_color_available,
    trump_available,
    decision_legal,
)


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
        self.winners: list[Player] = []

        self.trumps: list[Card] = [
            card
            for card in self.cards.full_deck
            if card.card_type in trump_types or card.card_color == trump_color
        ]
        self.trumps.reverse()
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

    def adjust_rank(self, player_cards: list[Card]) -> list[Card]:
        for card in player_cards:
            if card.card_name in [trump.card_name for trump in self.trumps]:
                card.card_rank += 100
                match card.card_color:
                    case Color.EICHEL:
                        card.card_rank += 0.8
                    case Color.GRUEN:
                        card.card_rank += 0.6
                    case Color.HERZ:
                        card.card_rank += 0.4
                    case Color.SCHELLEN:
                        card.card_rank += 0.2
            else:
                match card.card_color:
                    case Color.EICHEL:
                        card.card_rank += 80
                    case Color.GRUEN:
                        card.card_rank += 60
                    case Color.HERZ:
                        card.card_rank += 40
                    case Color.SCHELLEN:
                        card.card_rank += 20
        return player_cards

    def is_move_legal(self, player: Player, decision: Card) -> bool:
        lead = check_lead_card(lead_card=self.lead_card)
        call_sau = self.call_sau
        if lead:
            # Fehlt: Davonlaufen
            legal = True
            print("Lead-")
            if (
                    isinstance(self, Sauspiel)
                    and call_sau is not None
                    and check_player_owns_call_sau(player_cards=player.player_cards, call_sau=call_sau)
                    and decision.card_color == call_sau.card_color
                    and decision != call_sau
            ):
                legal = False
        elif (
                isinstance(self, Sauspiel)
                and call_sau is not None
                and check_player_owns_call_sau(player_cards=player.player_cards, call_sau=call_sau)
                and self.lead_card is not None
                and self.lead_card.card_color != call_sau.card_color
                and decision == call_sau
        ):
            legal = len(player.player_cards) == 1
        else:
            lead_card = self.lead_card
            assert lead_card is not None
            bool_lead_trump = check_lead_card_trump(lead_card=lead_card, trumps=self.trumps)
            if bool_lead_trump:
                trump_avail = trump_available(trumps=self.trumps, player_cards=player.player_cards)
                if trump_avail:
                    print("NoLead-LeadTrump-TrumpAvail-")
                    legal = decision_legal(decision=decision, legal_cards=self.trumps)
                else:
                    print("NoLead-LeadTrump-NoTrumpAvail-")
                    legal = True
            else:
                sim_col_avail = similar_color_available(
                    lead_card=lead_card, player_cards=player.player_cards, trumps=self.trumps
                )
                if sim_col_avail:
                    legal_cards = [
                        sim_color
                        for sim_color in player.player_cards
                        if sim_color.card_color == lead_card.card_color
                           and sim_color.card_name not in [trump.card_name for trump in self.trumps]
                    ]
                    if (
                            isinstance(self, Sauspiel)
                            and call_sau is not None
                            and check_player_owns_call_sau(
                        player_cards=player.player_cards, call_sau=call_sau
                    )
                            and lead_card.card_color == call_sau.card_color
                    ):
                        legal_cards = [call_sau]
                    print("NoLead-NoLeadTrump-SimColAvail-")
                    legal = decision_legal(decision=decision, legal_cards=legal_cards)
                else:
                    print("NoLead-NoLeadTrump-NoSimColAvail-")
                    legal = True
        print(f"The Move is {legal}")
        return legal

    def play_round(self) -> None:
        for player in self.players:
            player.card_decision(
                renderer=self.renderer,
                played_cards=self.played_cards,
                move_validator=lambda d, p=player: self.is_move_legal(player=p, decision=d),
            )
        strongest_card = find_strongest_card(
            played_cards=self.played_cards, trumps=self.trumps
        )
        winner_index = self.played_cards.index(strongest_card)
        for card in self.played_cards:
            self.players[winner_index].collected_cards.append(card)
        starter = self.players[winner_index]
        self.sort_players(starter=starter)
        for player in self.players:
            print(f"{player.player_name} has collected {player.collected_cards}")
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

    def check_multiple_most_point_teams(self) -> bool:
        most_point_teams = self.identify_most_points_teams()
        return len(most_point_teams) != 1

    def identify_game_winners(self) -> list[Player]:
        most_point_teams = self.identify_most_points_teams()
        winners: list[Player] = []
        if not self.check_multiple_most_point_teams():
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

    def check_player_has_trump(self, player: Player, trump: Card) -> bool:
        for card in player.player_cards:
            if card == trump:
                return True
        return False

    def check_team_has_trump(self, team: list[Player], trump: Card) -> bool:
        for player in team:
            if self.check_player_has_trump(player=player, trump=trump):
                return True
        return False

    def count_winners_runners(self) -> int:
        runners_count = 0
        for trump in self.trumps:
            if self.check_team_has_trump(team=self.winners, trump=trump):
                runners_count += 1
            else:
                break
        return runners_count

    @abstractmethod
    def calculate_game_value(self) -> int:
        pass

    def distribute_money(self, game_value: int) -> None:
        losers = [loser for loser in self.players if loser not in self.winners]
        winners_money = 0
        for loser in losers:
            loser.money -= game_value
            winners_money += game_value
        for winner in self.winners:
            winner.money += winners_money / len(self.winners)

    def play_game(self) -> None:
        for player in self.players:
            player.player_cards = self.adjust_rank(player_cards=player.player_cards)
            player.player_cards.sort(
                key=lambda sort_card: sort_card.card_rank, reverse=True
            )
        self.team_1.players.append(self.game_chooser)
        self.create_teams()
        print(f"Team 1: {self.team_1.players}")
        print(f"Team 2: {self.team_2.players}")
        print(f"Team 3: {self.team_3.players}")
        print(f"Team 4: {self.team_4.players}")
        for rounds in range(len(self.players[0].player_cards)):
            self.play_round()
        self.winners = self.identify_game_winners()
        game_value = self.calculate_game_value()
        self.distribute_money(game_value=game_value)
        print(f"The game winners are: {self.winners}")
        for player in self.players:
            print(f"{player} has {round(player.money)} cents")


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

    def calculate_game_value(self) -> int:
        game_value = 0
        if len(self.winners) == 4:
            game_value = 0
        elif len(self.winners) == 3:
            game_value = self.alone_price * 3
        elif len(self.winners) == 2 or len(self.winners) == 1:
            game_value = self.alone_price
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
        game_value += self.count_winners_runners() * self.base_price
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

    def adjust_rank(self, player_cards: list[Card]) -> list[Card]:
        for card in player_cards:
            if card.card_type == Type.OBER:
                card.card_rank = 3.5
        return super().adjust_rank(player_cards)

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.alone_price
        game_value += self.count_winners_runners() * self.base_price
        winning_team = self.find_players_team(player=self.winners[0])

        if winning_team.points == 120:
            game_value += 2 * self.base_price
        elif winning_team.points > 90 or (
                winning_team.points == 90 and self.game_chooser not in winning_team.players
        ):
            game_value += self.base_price

        if len(self.winners) == 3:
            game_value = game_value * 3

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
        game_value += self.count_winners_runners() * self.base_price
        winning_team = self.find_players_team(player=self.winners[0])

        if winning_team.points == 120:
            game_value += 2 * self.base_price
        elif winning_team.points > 90 or (
                winning_team.points == 90 and self.game_chooser not in winning_team.players
        ):
            game_value += self.base_price

        if len(self.winners) == 3:
            game_value = game_value * 3
        return game_value
