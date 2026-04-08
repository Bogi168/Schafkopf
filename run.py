from Classes.Renderer import ConsoleRenderer
from Classes.Schafkopf import Schafkopf

game = Schafkopf(
    renderer=ConsoleRenderer(), base_price=10, call_price=20, alone_price=50
)
game.main()
