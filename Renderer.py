from abc import abstractmethod, ABC
from Cards import Card


class Renderer(ABC):
    @abstractmethod
    def render(self, message: str) -> None:
        pass

    @abstractmethod
    def ask_player_name(self) -> str:
        pass

    @abstractmethod
    def reask_player_name(self) -> str:
        pass

    @abstractmethod
    def ask_player_game(self, player_name: str) -> str:
        pass

    @abstractmethod
    def reask_player_game(self, player_name: str) -> str:
        pass

    @abstractmethod
    def player_choose_game(self, player_name: str) -> str:
        pass

    @abstractmethod
    def player_rechoose_game(self, player_name: str) -> str:
        pass

    @abstractmethod
    def player_choose_sau_color(self) -> str:
        pass

    @abstractmethod
    def player_rechoose_sau_color(self) -> str:
        pass

    @abstractmethod
    def player_choose_solo_color(self) -> str:
        pass

    @abstractmethod
    def player_rechoose_solo_color(self) -> str:
        pass

    @abstractmethod
    def ask_player_card_decision(
        self, player_name: str, player_cards: list[Card]
    ) -> str:
        pass

    @abstractmethod
    def reask_player_card_decision(
        self, player_name: str, player_cards: list[Card]
    ) -> str:
        pass


class ConsoleRenderer(Renderer):
    def render(self, message: str) -> None:
        print(message)

    def ask_player_name(self) -> str:
        return input("Enter your name: ")

    def reask_player_name(self) -> str:
        return input("The name you entered is not valid! Enter your name: ")

    def ask_player_game(self, player_name: str) -> str:
        return input(f"{player_name}: Do you want to choose a game (Y/N): ").upper()

    def reask_player_game(self, player_name: str) -> str:
        return input(
            f"{player_name}: Your answer is not valid! Do you want to choose a game (Y/N): "
        ).upper()

    def player_choose_game(self, player_name: str) -> str:
        return input(
            f"{player_name}: Which game do you want to choose? (1: Sauspiel, 2: Wenz, 3: Solo): "
        ).upper()

    def player_rechoose_game(self, player_name: str) -> str:
        return input(
            f"{player_name}: Your answer is not valid! Which game do you want to choose? (1: Sauspiel, 2: Wenz, 3: Solo): "
        ).upper()

    def player_choose_sau_color(self) -> str:
        return input("Which color? (1: Eichel, 2: Grün, 3: Schellen): ")

    def player_rechoose_sau_color(self) -> str:
        return input(
            "Your answer is not valid! Which color? (1: Eichel, 2: Grün, 3: Schellen): "
        )

    def player_choose_solo_color(self) -> str:
        return input("Which color? (1: Eichel, 2: Grün, 3: Herz, 4: Schellen): ")

    def player_rechoose_solo_color(self) -> str:
        return input(
            "Your answer is not valid! Which color? (1: Eichel, 2: Grün, 3: Herz, 4: Schellen): "
        )

    def ask_player_card_decision(
        self, player_name: str, player_cards: list[Card]
    ) -> str:
        return input(
            f"{player_name}: Which card do you want to play? (1-{len(player_cards)}): "
        )

    def reask_player_card_decision(
        self, player_name: str, player_cards: list[Card]
    ) -> str:
        return input(
            f"{player_name}: That's not a legal move! Which card do you want to play? (1-{len(player_cards)}): "
        )
