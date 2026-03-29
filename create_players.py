from Player import Player

def create_players():
    players = []
    daniel = Player("Daniel")
    players.append(daniel)
    for x in range(3):
        players.append(Player(f"Bot {x+1}"))
    return players