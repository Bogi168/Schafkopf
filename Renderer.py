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
    def ask_player_decision(self, player_name):
        pass

    @abstractmethod
    def reask_player_decision(self, player_name):
        pass

class ConsoleRenderer(Renderer):
    def render(self, message):
        print(message)

    def ask_player_name(self):
        return input("Enter your name: ")

    def reask_player_name(self):
        return input("The name you entered is not valid! Enter your name: ")

    def ask_player_decision(self, player_name):
        return input(f"{player_name}: Which card do you want to play? (1-8): ")

    def reask_player_decision(self, player_name):
        return input(f"{player_name}: That's not valid! Which card do you want to play? (1-8): ")