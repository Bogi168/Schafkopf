from abc import abstractmethod, ABC
from pyexpat.errors import messages

from Cards import Card


class Renderer(ABC):
    @abstractmethod
    def render(self, message: str) -> None:
        pass

    @abstractmethod
    def ask_player_name(self, message: str) -> str:
        pass

    @abstractmethod
    def ask_player_decision(self, message: str) -> str:
        pass


class ConsoleRenderer(Renderer):
    def render(self, message: str) -> None:
        print(message)

    def ask_player_name(self, message) -> str:
        return input(message).capitalize()

    def ask_player_decision(self, message) -> str:
        return input(message).upper()
