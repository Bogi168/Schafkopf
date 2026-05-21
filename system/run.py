from system.Renderer import ConsoleRenderer
from game_classes.Schafkopf import Schafkopf

game = Schafkopf(
    renderer=ConsoleRenderer(), base_price=10, call_price=20, alone_price=30
)

if __name__ == "__main__":
    game.main()
