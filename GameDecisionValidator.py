from Renderer import Renderer
from Cards import Color, Type, Card, Cards
from Player import Player
from Game import Game, Sauspiel, Wenz, Solo, Ramsch
from text import (
    error_message,
    prompt_choose_game,
    prompt_choose_sau_color,
    prompt_choose_solo_color,
)


class GameDecisionValidator:
    def __init__(
        self,
        renderer: Renderer,
        cards: Cards,
        players: list[Player],
        game_choosers: list[Player],
        base_price: int,
        call_price: int,
        alone_price: int,
        amount_game_value_doublers: int,
    ):
        self.renderer = renderer
        self.cards = cards
        self.players = players
        self.game_choosers = game_choosers
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price
        self.amount_game_value_doublers = amount_game_value_doublers
        self.playable_games: list[type[Game]] = [Sauspiel, Wenz, Solo]
        self.game_chooser: None | Player = None

    @staticmethod
    def is_player_quits(quitting_possible: bool, decision: str) -> bool:
        quitting_code_words = ["QUIT", "Q"]
        return quitting_possible and decision in quitting_code_words

    @staticmethod
    def count_color_cards(
        player_cards: list[Card], color: Color, trump_types: list[Type]
    ) -> int:
        count = 0
        for card in player_cards:
            if card.card_color == color and card.card_type not in trump_types:
                count += 1
        return count

    @staticmethod
    def is_player_owns_sau(sau_color: Color, player_cards: list[Card]) -> bool:
        return any(
            (card.card_color == sau_color and card.card_type == Type.SAU)
            for card in player_cards
        )

    def is_sauspiel_playable(self, player_cards: list[Card]) -> bool:
        colors = (Color.EICHEL, Color.GRUEN, Color.SCHELLEN)
        eichel_count = 0
        gruen_count = 0
        schellen_count = 0

        for card_color in colors:
            match card_color:
                case Color.EICHEL:
                    eichel_count = self.count_color_cards(
                        player_cards=player_cards,
                        color=card_color,
                        trump_types=[Type.OBER, Type.UNTER],
                    )
                case Color.GRUEN:
                    gruen_count = self.count_color_cards(
                        player_cards=player_cards,
                        color=card_color,
                        trump_types=[Type.OBER, Type.UNTER],
                    )
                case Color.SCHELLEN:
                    schellen_count = self.count_color_cards(
                        player_cards=player_cards,
                        color=card_color,
                        trump_types=[Type.OBER, Type.UNTER],
                    )

        for color in colors:
            if self.is_player_owns_sau(color, player_cards=player_cards):
                match color:
                    case Color.EICHEL:
                        eichel_count = 0
                    case Color.GRUEN:
                        gruen_count = 0
                    case Color.SCHELLEN:
                        schellen_count = 0

        return eichel_count + gruen_count + schellen_count != 0

    def get_available_game_decisions(
        self,
        playable_games: list[type[Game]],
        prev_game: Game | None,
        player_cards: list[Card],
    ) -> list[type[Game]]:
        if prev_game is None:
            prev_game_rank = 0
        else:
            prev_game_rank = prev_game.rank

        if prev_game_rank != 0:
            available_games: list[type[Game]] = [
                game for game in playable_games if game.rank > prev_game_rank
            ]
        else:
            color_available: bool = self.is_sauspiel_playable(player_cards=player_cards)
            if color_available:
                available_games: list[type[Game]] = [game for game in playable_games]
            else:
                available_games: list[type[Game]] = [
                    game for game in playable_games if game.rank != Sauspiel.rank
                ]
        return available_games

    def get_available_sau_color_decisions(
        self, player_cards: list[Card], playable_colors: list[Color]
    ) -> list[Color]:
        for color in playable_colors.copy():
            player_has_sau = self.is_player_owns_sau(
                player_cards=player_cards, sau_color=color
            )
            color_count = self.count_color_cards(
                player_cards=player_cards,
                color=color,
                trump_types=[Type.OBER, Type.UNTER],
            )
            if color_count == 0 or player_has_sau:
                playable_colors.remove(color)
        return playable_colors

    def choose_game_decision(
        self, player: Player, prev_game: Game | None, quitting_possible: bool = False
    ) -> Game | None:
        game = None
        player_name = player.player_name
        player_cards = player.player_cards
        available_decisions = self.get_available_game_decisions(
            playable_games=self.playable_games,
            prev_game=prev_game,
            player_cards=player_cards,
        )
        games = {
            "1": Sauspiel,
            "2": Wenz,
            "3": Solo,
        }
        valid_inputs = [
            key for key, game in games.items() if game in available_decisions
        ]
        decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_game(
                player_name=player_name, quitting_possible=quitting_possible
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in valid_inputs
            or self.is_player_quits(quitting_possible=quitting_possible, decision=x),
        )
        if decision == "QUIT":
            decision = "Q"
        if decision != "Q":
            self.game_chooser = player
        match decision:
            case "Q":
                return prev_game
            case "1":
                sau_colors = [Color.EICHEL, Color.GRUEN, Color.SCHELLEN]
                available_colors = self.get_available_sau_color_decisions(
                    player_cards=player_cards, playable_colors=sau_colors.copy()
                )
                color_mapping = {
                    "1": Color.EICHEL,
                    "2": Color.GRUEN,
                    "3": Color.SCHELLEN,
                }

                valid_inputs = [
                    key
                    for key, color in color_mapping.items()
                    if color in available_colors
                ]

                sau_color_decision = self.renderer.ask_with_validation(
                    prompt=prompt_choose_sau_color(player_name=player_name),
                    error_prefix=error_message,
                    preprocess=lambda x: x.strip(),
                    validator=lambda x: x in valid_inputs,
                )
                sau_color = color_mapping[sau_color_decision]
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
                trump_color = self.renderer.ask_with_validation(
                    prompt=prompt_choose_solo_color(player_name=player_name),
                    error_prefix=error_message,
                    preprocess=lambda x: x.strip(),
                    validator=lambda x: x in ("1", "2", "3", "4"),
                )
                match trump_color:
                    case "1":
                        trump_color = Color.EICHEL
                    case "2":
                        trump_color = Color.GRUEN
                    case "3":
                        trump_color = Color.HERZ
                    case "4":
                        trump_color = Color.SCHELLEN
                    case _:
                        trump_color = Color.HERZ

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
                    game = self.choose_game_decision(player=player, prev_game=game)
                elif game.rank == Solo.rank:
                    break
                elif game.rank > Sauspiel.rank:
                    game = self.choose_game_decision(
                        player=player, prev_game=game, quitting_possible=True
                    )
                else:
                    game = self.choose_game_decision(player=player, prev_game=game)
        return game
