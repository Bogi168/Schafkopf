from Renderer import ConsoleRenderer
from Schafkopf import Schafkopf

game = Schafkopf(
    renderer=ConsoleRenderer(), base_price=10, call_price=20, alone_price=50
)
game.main()
