from __future__ import annotations
import random

from system.Renderer import Renderer
from card_classes.Cards import Cards, Color
from player_classes.Player import Player, Bot
from game_classes.Game import Game, Sauspiel, Wenz, Solo, Ramsch
from input_validators.GameDecisionValidator import GameDecisionValidator
from card_classes.CardPowerCalculator import SauspielCardPowerCalculator
from system.custom_exceptions import GamemodeIsNotImplementedError
from system.text import (
    error_message,
    prompt_player_name,
    prompt_play_again_message,
    show_player_cards,
    words_of_thanks,
)


class Schafkopf:
    def __init__(
        self, renderer: Renderer, base_price: int, call_price: int, alone_price: int
    ) -> None:
        self.players: list[Player] = []
        self.starter: Player | None = None
        self.game_choosers: list[Player] = []
        self.amount_game_value_doubles = 0

        self.cards = Cards()
        self.renderer = renderer
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price

        self.game_mapping: dict[type[Game], bool] = Game.game_mapping.copy()
        self.choosable_game_mapping: dict[type[Game], bool] = {
            game_mode: is_choosable
            for game_mode, is_choosable in self.game_mapping.items()
            if is_choosable
        }
        self.game_rank_mapping: dict[type[Game], int] = {
            game: rank
            for rank, game in enumerate(self.choosable_game_mapping.keys(), start=1)
        }
        self.game_decision_validator: GameDecisionValidator = GameDecisionValidator(
            choosable_game_mapping=self.choosable_game_mapping,
            game_rank_mapping=self.game_rank_mapping,
        )

    def _create_players(self) -> list[Player]:
        players: list[Player] = []

        player_name = self.renderer.ask_with_validation(
            prompt=prompt_player_name,
            error_prefix=error_message,
            preprocess=lambda x: x.strip().capitalize(),
            validator=lambda x: x != "",
        )
        players.append(
            Player(
                player_name=player_name,
                renderer=self.renderer,
                game_decision_validator=self.game_decision_validator,
            )
        )
        for i in range(3):
            players.append(
                Bot(
                    bot_name=f"Bot {i + 1}",
                    renderer=self.renderer,
                    game_decision_validator=self.game_decision_validator,
                )
            )

        return players

    def sort_players(self, starter: Player) -> None:
        starter_index = self.players.index(starter)
        self.players = self.players[starter_index:] + self.players[:starter_index]

    def deal_cards(self, cards_amount_per_player: int) -> None:
        random.shuffle(self.cards.deck)
        for player in self.players:
            player.player_cards.extend(self.cards.deck[-cards_amount_per_player:])
            del self.cards.deck[-cards_amount_per_player:]

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
        self.amount_game_value_doubles = 0
        for player in self.players:
            if player.is_doubles_game_value():
                self.amount_game_value_doubles += 1
        self.deal_cards(cards_amount_per_player=cards_per_player_per_dealing_round)
        self.sort_player_hands()

    def prepare_players(self):
        assert self.starter is not None
        self.sort_players(starter=self.starter)
        self.game_choosers.clear()

    # sort cards for a Sauspiel -> easier to make game decisions
    def sort_player_hands(self) -> None:
        card_power_calculator = SauspielCardPowerCalculator()
        for player in self.players:
            player.player_cards.sort(
                key=card_power_calculator.get_card_power, reverse=True
            )

    def get_game(self, game_mode: type[Game], player: Player) -> Game:
        kwargs = dict(
            cards=self.cards,
            renderer=self.renderer,
            players=self.players,
            game_chooser=player,
            base_price=self.base_price,
            amount_game_value_doubles=self.amount_game_value_doubles,
        )
        if game_mode is Sauspiel:
            sau_color: Color = player.get_sau_color()
            kwargs.update(call_price=self.call_price, sau_color=sau_color)  # type: ignore

        elif game_mode is Wenz:
            kwargs["alone_price"] = self.alone_price

        elif game_mode is Solo:
            trump_color = player.get_trump_color()
            kwargs.update(trump_color=trump_color, alone_price=self.alone_price)  # type: ignore

        else:
            raise GamemodeIsNotImplementedError(f"{game_mode} is not implemented yet")

        return game_mode(**kwargs)

    def players_choose_game(self) -> Game:
        game_mode: type[Game] | None = None
        game: Game | None = None
        if not self.game_choosers:
            return Ramsch(
                cards=self.cards,
                renderer=self.renderer,
                players=self.players,
                alone_price=self.alone_price,
                amount_game_value_doubles=self.amount_game_value_doubles,
            )
        else:
            for player in self.game_choosers:
                if game_mode is None:
                    decision: type[Game] | None = player.choose_game_mode(
                        prev_game_mode=game_mode,
                    )
                    assert decision is not None
                    game_mode: type[Game] = decision
                    game: Game = self.get_game(game_mode=game_mode, player=player)

                elif game_mode == Solo:
                    assert game is not None
                    return game

                elif (
                    game_mode is not None
                    and self.game_rank_mapping[game_mode]
                    > self.game_rank_mapping[Sauspiel]
                ):
                    decision: type[Game] | None = player.choose_game_mode(
                        prev_game_mode=game_mode,
                        quitting_possible=True,
                    )
                    if decision is None:
                        continue
                    else:
                        game_mode: type[Game] = decision
                        game: Game = self.get_game(game_mode=game_mode, player=player)

                else:
                    decision: type[Game] | None = player.choose_game_mode(
                        prev_game_mode=game_mode,
                    )
                    assert decision is not None
                    game_mode: type[Game] = decision
                    game: Game = self.get_game(game_mode=game_mode, player=player)
        assert game is not None
        return game

    def get_new_starter(self, prev_starter_index: int) -> Player:
        if self.players[prev_starter_index] == self.players[-1]:
            return self.players[0]
        else:
            return self.players[prev_starter_index + 1]

    def main(self) -> None:
        self.players = self._create_players()
        self.starter: Player = random.choice(self.players)
        while True:
            self.prepare_players()
            self.prepare_cards()
            for player in self.players:
                self.renderer.render(
                    message=show_player_cards(
                        player_name=player.player_name, player_cards=player.player_cards
                    )
                )
                if player.is_chooses_game():
                    self.game_choosers.append(player)
            game: Game = self.players_choose_game()
            game.play_game()
            assert self.starter is not None
            self.starter = self.get_new_starter(
                prev_starter_index=self.players.index(self.starter)
            )
            play_again = self.renderer.ask_with_validation(
                prompt=prompt_play_again_message,
                error_prefix=error_message,
                preprocess=lambda x: x.strip().upper(),
                validator=lambda x: x in ("YES", "Y", "NO", "N"),
            )
            if play_again in ("NO", "N"):
                break

        self.renderer.render(message=words_of_thanks)
