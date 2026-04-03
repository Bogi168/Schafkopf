class Team:
    def __init__(self, team_name):
        self.team_name = team_name
        self.players = []

    def __repr__(self):
        return self.team_name

    @property
    def points(self):
        points = 0
        for player in self.players:
            for player_card in player.collected_cards:
                points += player_card.card_type.points
        return points