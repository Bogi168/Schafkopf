import random
from Renderer import Renderer
from Cards import Cards, Color, Type, Card
from Player import Player, Bot
from Game import Game, Sauspiel, Wenz, Solo, Ramsch


class Schafkopf:
    def __init__(
        self, renderer: Renderer, base_price: int, call_price: int, alone_price: int
    ) -> None:
        self.playable_games: list[type[Game]] = [Sauspiel, Wenz, Solo]
        self.players: list[Player] = []
        self.starter: Player | None = None
        self.game_choosers: list[Player] = []
        self.game_chooser: Player | None = None
        self.game_mode: Game | None = None

        self.cards = Cards()
        self.renderer = renderer
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price

    def _create_players(self) -> list[Player]:
        player_name = self.renderer.ask_player_name()
        if player_name == "":
            player_name = self.renderer.reask_player_name()
        players = [Player(player_name=player_name)]
        for i in range(3):
            players.append(Bot(f"Bot {i + 1}"))
        return players

    def _ask_player_game_decision(self, player: Player) -> None:
        decision = self.renderer.ask_player_game(player_name=player.player_name)
        while decision not in ("YES", "Y", "NO", "N"):
            decision = self.renderer.reask_player_game(player_name=player.player_name)
        if decision in ("YES", "Y"):
            self.game_choosers.append(player)

    @staticmethod
    def choose_starter(players: list[Player]) -> Player:
        starter = random.choice(players)
        return starter

    @staticmethod
    def sort_players(players: list[Player], starter: Player) -> list[Player]:
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

    def deal_cards(self, deck: list[Card], players: list[Player]) -> list[Card]:
        deck = self.shuffle_cards(cards=deck)
        for player_num in range(len(players)):
            for _ in range(4):
                card = deck[-1]
                players[player_num].player_cards.append(card)
                deck.pop(-1)
        return deck

    def prepare_cards(self, players: list[Player], deck: list[Card]) -> list[Card]:
        for player in players:
            player.player_cards.clear()
            player.collected_cards.clear()
        deck = self.deal_cards(deck=deck, players=players)
        # Fehlt: Legen
        deck = self.deal_cards(deck=deck, players=players)
        return deck

    # sort cards for a Sauspiel -> easier to make game decisions
    @staticmethod
    def get_card_power(card: Card) -> int:
        power = 0
        trump_type_power = 1000
        trump_color_power = 100
        eichel_power = 80
        gruen_power = 60
        herz_power = 40
        schellen_power = 20

        trump_color = Color.HERZ
        trump_types = [Type.OBER, Type.UNTER]

        if card.card_type not in trump_types and card.card_color == trump_color:
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

        for trump_type in trump_types:
            if card.card_type == trump_type:
                power += trump_type_power
                return power
            else:
                trump_type_power -= 100

        return power

    def sort_player_hands(self) -> None:
        for player in self.players:
            player.player_cards.sort(key=self.get_card_power, reverse=True)

    @staticmethod
    def is_player_quits(quitting_possible: bool, decision: str) -> bool:
        quitting_code_words = ["QUIT", "Q"]
        player_quits = False
        if quitting_possible and decision in quitting_code_words:
            player_quits = True
        return player_quits

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
        player_has_sau = False
        for card in player_cards:
            if card.card_color == sau_color and card.card_type == Type.SAU:
                player_has_sau = True
        return player_has_sau

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

    def check_available_game_decisions(
        self,
        playable_games: list[type[Game]],
        prev_game: Game | None,
        player_cards: list[Card],
    ) -> list[str]:
        if prev_game is None:
            prev_game_rank = 0
        else:
            prev_game_rank = prev_game.rank

        if prev_game_rank != 0:
            available_game_ranks = [
                str(game.rank) for game in playable_games if game.rank > prev_game_rank
            ]
        else:
            color_available = self.is_sauspiel_playable(player_cards=player_cards)
            if color_available:
                available_game_ranks = [str(game.rank) for game in playable_games]
            else:
                available_game_ranks = [
                    str(game.rank) for game in playable_games if game.rank != 1
                ]
        return available_game_ranks

    def check_available_sau_color_decisions(
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

    @staticmethod
    def convert_sau_color_value(decision: str) -> int:
        sau_color_decision: int
        match decision:
            case "1":
                sau_color_decision = 1
            case "2":
                sau_color_decision = 2
            case "3":
                sau_color_decision = 4
            case _:
                sau_color_decision = -1
        return sau_color_decision

    @staticmethod
    def convert_sau_color_index(decision: str) -> int:
        sau_color_decision: int
        match decision:
            case "1":
                sau_color_decision = 0
            case "2":
                sau_color_decision = 1
            case "3":
                sau_color_decision = 2
            case _:
                sau_color_decision = -1
        return sau_color_decision

    def choose_game_decision(
        self, player: Player, prev_game: Game | None, quitting_possible: bool = False
    ) -> str:
        player_name = player.player_name
        player_cards = player.player_cards
        available_decisions = self.check_available_game_decisions(
            playable_games=self.playable_games,
            prev_game=prev_game,
            player_cards=player_cards,
        )
        decision = self.renderer.player_choose_game(player_name)
        while decision not in available_decisions and not self.is_player_quits(
            quitting_possible=quitting_possible, decision=decision
        ):
            decision = self.renderer.player_rechoose_game(player_name=player_name)
        if decision == "QUIT":
            decision = "Q"
        if decision != "Q":
            self.game_chooser = player
        match decision:
            case "Q":
                pass
            case "1":
                sau_colors = [Color.EICHEL, Color.GRUEN, Color.SCHELLEN]
                available_colors = self.check_available_sau_color_decisions(
                    player_cards=player_cards, playable_colors=sau_colors.copy()
                )
                sau_color_decision = self.renderer.player_choose_sau_color()
                sau_color_value = self.convert_sau_color_value(
                    decision=sau_color_decision
                )
                sau_color_index = self.convert_sau_color_index(
                    decision=sau_color_decision
                )
                while (
                    sau_color_value not in [color.value for color in sau_colors]
                    or sau_colors[sau_color_index] not in available_colors
                ):
                    sau_color_decision = self.renderer.player_rechoose_sau_color()
                    sau_color_value = self.convert_sau_color_value(
                        decision=sau_color_decision
                    )
                    sau_color_index = self.convert_sau_color_index(
                        decision=sau_color_decision
                    )
                sau_color = sau_colors[sau_color_index]
                self.game_mode = Sauspiel(
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
                self.game_mode = Wenz(
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    call_price=self.call_price,
                    alone_price=self.alone_price,
                )
            case "3":
                trump_color = self.renderer.player_choose_solo_color()
                while trump_color not in ("1", "2", "3", "4"):
                    trump_color = self.renderer.player_rechoose_solo_color()
                match trump_color:
                    case "1":
                        trump_color = Color.EICHEL
                    case "2":
                        trump_color = Color.GRUEN
                    case "3":
                        trump_color = Color.HERZ
                    case "4":
                        trump_color = Color.SCHELLEN
                self.game_mode = Solo(
                    trump_color=trump_color,
                    cards=self.cards,
                    renderer=self.renderer,
                    players=self.players,
                    game_chooser=self.game_chooser,
                    base_price=self.base_price,
                    call_price=self.call_price,
                    alone_price=self.alone_price,
                )
        return decision

    def players_choose_game(self) -> None:
        if len(self.game_choosers) == 0:
            self.game_mode = Ramsch(
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
                if self.game_mode is None:
                    self.choose_game_decision(player=player, prev_game=self.game_mode)
                elif self.game_mode.rank == 3:
                    pass
                elif self.game_mode.rank > 1:
                    self.choose_game_decision(
                        player=player, prev_game=self.game_mode, quitting_possible=True
                    )
                else:
                    self.choose_game_decision(player=player, prev_game=self.game_mode)

    def main(self) -> None:
        self.players = self._create_players()
        self.starter = self.choose_starter(players=self.players)
        self.players = self.sort_players(players=self.players, starter=self.starter)
        self.cards.deck = self.prepare_cards(players=self.players, deck=self.cards.deck)
        self.sort_player_hands()
        for player in self.players:
            print(player.player_cards)
            self._ask_player_game_decision(player=player)
        self.players_choose_game()
        self.game_mode.play_game()
        self.cards.reset_deck()
