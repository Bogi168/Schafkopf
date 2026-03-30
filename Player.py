class Player:
    def __init__(self, player_name):
        self.player_name = player_name
        self.player_cards = []
        self.bool_beginner = False

    def __repr__(self):
        return self.player_name

    def decision(self):
        pass