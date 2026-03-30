from Renderer import Renderer

class Player:
    def __init__(self, player_name):
        self.player_name = player_name
        self.player_cards = []
        self.collected_cards = []
        self.bool_beginner = False

    def __repr__(self):
        return self.player_name

    def bool_valid_number(self, decision) -> bool:
        if decision in ("1", "2", "3", "4", "5", "6", "7", "8") and int(decision) <= len(self.player_cards):
            return True
        else:
            return False


    def decision(self, renderer: Renderer):
        print(self.player_cards)
        decision = renderer.ask_player_decision(self.player_name)
        while not self.bool_valid_number(decision):
            decision = renderer.reask_player_decision(self.player_name)
            if self.bool_valid_number(decision):
                break