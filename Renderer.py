from abc import abstractmethod, ABC

class Renderer(ABC):
    @abstractmethod
    def render(self, message):
        pass

    @abstractmethod
    def ask_player_name(self):
        pass

    @abstractmethod
    def reask_player_name(self):
        pass

    @abstractmethod
    def ask_player_decision(self, player_name, player_cards):
        pass

    @abstractmethod
    def reask_player_decision(self, player_name, player_cards):
        pass

class ConsoleRenderer(Renderer):
    def render(self, message):
        print(message)

    def ask_player_name(self):
        return input("Enter your name: ")

    def reask_player_name(self):
        return input("The name you entered is not valid! Enter your name: ")

    def ask_player_decision(self, player_name, player_cards):
        return input(f"{player_name}: Which card do you want to play? (1-{len(player_cards)}): ")

    def reask_player_decision(self, player_name, player_cards):
        return input(f"{player_name}: That's not a legal move! Which card do you want to play? (1-{len(player_cards)}): ")