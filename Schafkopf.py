import random
from Renderer import Renderer
from Cards import Cards, Color, Type, Card
from Player import Player, Bot
from Card_Power_Calculator import Sauspiel_Card_Power_Calculator
from Game import Game, Sauspiel, Wenz, Solo, Ramsch
from text import (
    error_message,
    prompt_games_amount,
    prompt_player_name,
    prompt_play_again_message,
    prompt_ask_to_choose_game,
    prompt_choose_game,
    prompt_choose_sau_color,
    prompt_choose_solo_color,
    show_player_cards,
    words_of_thanks,
)


class Schafkopf:
    def __init__(
        self, renderer: Renderer, base_price: int, call_price: int, alone_price: int
    ) -> None:
        self.playable_games: list[type[Game]] = [Sauspiel, Wenz, Solo]
        self.players: list[Player] = []
        self.starter: Player | None = None
        self.game_choosers: list[Player] = []
        self.game_chooser: Player | None = None

        self.cards = Cards()
        self.renderer = renderer
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price

    def _create_players(self) -> list[Player]:
        player_name = self.renderer.ask_with_validation(
            prompt=prompt_player_name,
            error_prefix=error_message,
            preprocess=lambda x: x.strip().capitalize(),
            validator=lambda x: x != "",
        )
        players = [Player(player_name=player_name)]
        for i in range(3):
            players.append(Bot(f"Bot {i + 1}"))
        return players

    def _ask_player_game_decision(self, player: Player) -> None:
        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_to_choose_game(player_name=player.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in ("YES", "Y", "NO", "N"),
        )
        if decision in ("YES", "Y"):
            self.game_choosers.append(player)

    @staticmethod
    def choose_starter(players: list[Player]) -> Player:
        starter = random.choice(players)
        return starter

    @staticmethod
    def get_sorted_players(players: list[Player], starter: Player) -> list[Player]:
        found_beginner = False
        while not found_beginner:
            player = players[0]
            if not player == starter:
                players.append(player)
                players.pop(0)
            else:
                found_beginner = True
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
        # Fehlt: Legen
        self.deal_cards(cards_amount_per_player=cards_per_player_per_dealing_round)

    def prepare_players(self):
        self.sort_player_hands()
        self.players = self.get_sorted_players(
            players=self.players, starter=self.starter
        )
        self.game_chooser = None
        self.game_choosers.clear()

    # sort cards for a Sauspiel -> easier to make game decisions
    def sort_player_hands(self) -> None:
        card_power_calculator = Sauspiel_Card_Power_Calculator()
        for player in self.players:
            player.player_cards.sort(
                key=card_power_calculator.get_card_power, reverse=True
            )

    @staticmethod
    def is_player_quits(quitting_possible: bool, decision: str) -> bool:
        quitting_code_words = ["QUIT", "Q"]
        if quitting_possible and decision in quitting_code_words:
            return True
        return False

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
    def is_player_has_sau(sau_color: Color, player_cards: list[Card]) -> bool:
        for card in player_cards:
            if card.card_color == sau_color and card.card_type == Type.SAU:
                return True
        return False

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
            if self.is_player_has_sau(color, player_cards=player_cards):
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
            player_has_sau = self.is_player_has_sau(
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
                    alone_price=self.alone_price,
                    sau_color=sau_color,
                )
            case "2":
                game = Wenz(
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    call_price=self.call_price,
                    alone_price=self.alone_price,
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
                    call_price=self.call_price,
                    alone_price=self.alone_price,
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
                base_price=self.base_price,
                call_price=self.call_price,
                alone_price=self.alone_price,
            )
        else:
            for player in self.game_choosers:
                if game is None:
                    game = self.choose_game_decision(player=player, prev_game=game)
                elif game.rank == Solo.rank:
                    break
                elif game.rank >= Sauspiel.rank:
                    game = self.choose_game_decision(
                        player=player, prev_game=game, quitting_possible=True
                    )
                else:
                    game = self.choose_game_decision(player=player, prev_game=game)
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
            self.prepare_cards()
            self.prepare_players()
            for player in self.players:
                self.renderer.render(
                    message=show_player_cards(
                        player_name=player.player_name, player_cards=player.player_cards
                    )
                )
                self._ask_player_game_decision(player=player)
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
