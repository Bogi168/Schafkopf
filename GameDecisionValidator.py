from Cards import Color, Type, Card
from Game import Game, Sauspiel, Wenz, Solo


class GameDecisionValidator:
    def __init__(self):
        self.game_mapping = {
            "1": Sauspiel,
            "2": Wenz,
            "3": Solo,
        }
        self.sau_color_mapping = {
            "1": Color.EICHEL,
            "2": Color.GRUEN,
            "3": Color.SCHELLEN,
        }
        self.solo_trump_color_mapping = {
            "1": Color.EICHEL,
            "2": Color.GRUEN,
            "3": Color.HERZ,
            "4": Color.SCHELLEN,
        }

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

    def get_available_game_modes(
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
            available_game_modes: list[type[Game]] = [
                game for game in playable_games if game.rank > prev_game_rank
            ]
        else:
            color_available: bool = self.is_sauspiel_playable(player_cards=player_cards)
            if color_available:
                available_game_modes: list[type[Game]] = [
                    game for game in playable_games
                ]
            else:
                available_game_modes: list[type[Game]] = [
                    game for game in playable_games if game.rank != Sauspiel.rank
                ]
        return available_game_modes

    def get_valid_game_mode_decisions(
        self, prev_game: Game | None, player_cards: list[Card]
    ) -> list[str]:
        available_game_modes = self.get_available_game_modes(
            playable_games=[game for game in self.game_mapping.values()],
            prev_game=prev_game,
            player_cards=player_cards,
        )
        valid_inputs = [
            key
            for key, game in self.game_mapping.items()
            if game in available_game_modes
        ]
        return valid_inputs

    def get_available_sau_color_decisions(
        self, player_cards: list[Card], sau_colors: list[Color]
    ) -> list[Color]:
        playable_colors = sau_colors.copy()
        for color in playable_colors:
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

    def get_valid_call_sau_colors(self, player_cards: list[Card]) -> list[str]:
        sau_colors = [color for key, color in self.sau_color_mapping.items()]
        available_colors = self.get_available_sau_color_decisions(
            player_cards=player_cards, sau_colors=sau_colors
        )
        valid_inputs = [
            key
            for key, color in self.sau_color_mapping.items()
            if color in available_colors
        ]
        return valid_inputs

    def get_valid_solo_trump_colors(self) -> list[str]:
        valid_inputs = [key for key in self.solo_trump_color_mapping.keys()]
        return valid_inputs
