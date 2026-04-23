from __future__ import annotations
from typing import TYPE_CHECKING
import random
from Renderer import Renderer
from Cards import Cards
from Player import Player, Bot
from Game import Game, Sauspiel, Wenz, Solo, Ramsch
from CardPowerCalculator import SauspielCardPowerCalculator
from text import (
    error_message,
    prompt_games_amount,
    prompt_player_name,
    prompt_play_again_message,
    show_player_cards,
    words_of_thanks,
)

if TYPE_CHECKING:
    from Cards import Card


class Schafkopf:
    def __init__(
        self, renderer: Renderer, base_price: int, call_price: int, alone_price: int
    ) -> None:
        self.players: list[Player] = []
        self.starter: Player | None = None
        self.game_chooser: Player | None = None
        self.game_choosers: list[Player] = []
        self.amount_game_value_doublers = 0

        self.cards = Cards()
        self.renderer = renderer
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price

        self.game_mapping = {
            "1": Sauspiel,
            "2": Wenz,
            "3": Solo,
        }

    def _create_players(self) -> list[Player]:
        player_name = self.renderer.ask_with_validation(
            prompt=prompt_player_name,
            error_prefix=error_message,
            preprocess=lambda x: x.strip().capitalize(),
            validator=lambda x: x != "",
        )
        players = [
            Player(
                player_name=player_name,
                renderer=self.renderer,
                game_mapping=self.game_mapping,
            )
        ]
        for i in range(3):
            players.append(
                Bot(
                    bot_name=f"Bot {i + 1}",
                    renderer=self.renderer,
                    game_mapping=self.game_mapping,
                )
            )
        return players

    @staticmethod
    def choose_starter(players: list[Player]) -> Player:
        starter = random.choice(players)
        return starter

    @staticmethod
    def get_sorted_players(players: list[Player], starter: Player) -> list[Player]:
        starter_index = players.index(starter)
        players = players[starter_index:] + players[:starter_index]
        return players

    @staticmethod
    def shuffle_cards(cards: list[Card]) -> list[Card]:
        random.shuffle(cards)
        return cards

    def deal_cards(self, cards_amount_per_player: int) -> None:
        self.shuffle_cards(cards=self.cards.deck)
        for player in self.players:
            for _ in range(cards_amount_per_player):
                card = self.cards.deck[-1]
                player.player_cards.append(card)
                self.cards.deck.pop(-1)

    def prepare_cards(self) -> None:
        for player in self.players:
            player.player_cards.clear()
            player.collected_cards.clear()
        self.cards.reset_deck()
        cards_per_dealing_round = len(self.cards.deck) // 2
        cards_per_player_per_dealing_round = cards_per_dealing_round // len(
            self.players
        )
        self.deal_cards(cards_amount_per_player=cards_per_player_per_dealing_round)
        self.sort_player_hands()
        self.amount_game_value_doublers = 0
        for player in self.players:
            self.renderer.render(
                message=show_player_cards(
                    player_name=player.player_name, player_cards=player.player_cards
                )
            )
            self.amount_game_value_doublers = player.ask_double_game_value(
                amount_game_value_doublers=self.amount_game_value_doublers,
            )
        self.deal_cards(cards_amount_per_player=cards_per_player_per_dealing_round)
        self.sort_player_hands()

    def prepare_players(self):
        self.players = self.get_sorted_players(
            players=self.players, starter=self.starter
        )
        self.game_choosers.clear()

    # sort cards for a Sauspiel -> easier to make game decisions
    def sort_player_hands(self) -> None:
        card_power_calculator = SauspielCardPowerCalculator()
        for player in self.players:
            player.player_cards.sort(
                key=card_power_calculator.get_card_power, reverse=True
            )

    def get_game(self, decision: str, player: Player, prev_game: Game | None) -> Game:
        game: Game | None = None
        if decision != "Q":
            self.game_chooser = player
        match decision:
            case "Q":
                return prev_game
            case "1":
                sau_color = player.get_sau_color()
                game = Sauspiel(
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    call_price=self.call_price,
                    amount_game_value_doublers=self.amount_game_value_doublers,
                    sau_color=sau_color,
                )
            case "2":
                game = Wenz(
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    alone_price=self.alone_price,
                    amount_game_value_doublers=self.amount_game_value_doublers,
                )
            case "3":
                trump_color = player.get_trump_color()
                game = Solo(
                    trump_color=trump_color,
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    alone_price=self.alone_price,
                    amount_game_value_doublers=self.amount_game_value_doublers,
                )
        return game

    def players_choose_game(self) -> Game:
        game: None | Game = None
        if len(self.game_choosers) == 0:
            game = Ramsch(
                cards=self.cards,
                renderer=self.renderer,
                players=self.players,
                game_chooser=self.game_chooser,
                alone_price=self.alone_price,
                amount_game_value_doublers=self.amount_game_value_doublers,
            )
        else:
            for player in self.game_choosers:
                if game is None:
                    decision = player.choose_game_mode(
                        prev_game=game,
                    )
                elif game.rank == Solo.rank:
                    break
                elif game.rank > Sauspiel.rank:
                    decision = player.choose_game_mode(
                        prev_game=game,
                        quitting_possible=True,
                    )
                else:
                    decision = player.choose_game_mode(
                        prev_game=game,
                    )
                game = self.get_game(decision=decision, player=player, prev_game=game)
        return game

    def get_new_starter(self, prev_starter_index: int) -> Player:
        if self.players[prev_starter_index] == self.players[-1]:
            return self.players[0]
        else:
            return self.players[prev_starter_index + 1]

    def main(self) -> None:
        self.players = self._create_players()
        self.starter = self.choose_starter(players=self.players)
        games_amount: str = self.renderer.ask_with_validation(
            prompt=prompt_games_amount,
            error_prefix=error_message,
            validator=lambda x: x.isdigit() and int(x) > 0,
            preprocess=lambda x: x.strip(),
        )
        for game_num in range(int(games_amount)):
            self.prepare_players()
            self.prepare_cards()
            for player in self.players:
                self.renderer.render(
                    message=show_player_cards(
                        player_name=player.player_name, player_cards=player.player_cards
                    )
                )
                self.game_choosers = player.ask_choose_decision(
                    game_choosers=self.game_choosers
                )
            game = self.players_choose_game()
            assert game is not None
            game.play_game()
            self.starter = self.get_new_starter(
                prev_starter_index=self.players.index(self.starter)
            )
            if game_num != int(games_amount) - 1:
                play_again = self.renderer.ask_with_validation(
                    prompt=prompt_play_again_message,
                    error_prefix=error_message,
                    preprocess=lambda x: x.strip().upper(),
                    validator=lambda x: x in ("YES", "Y", "NO", "N"),
                )
                if play_again in ("NO", "N"):
                    break

        self.renderer.render(message=words_of_thanks)
