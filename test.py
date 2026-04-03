from Renderer import ConsoleRenderer
from Schafkopf import Schafkopf

renderer = ConsoleRenderer()
schafkopf = Schafkopf(renderer = renderer, base_price=10, call_price=20, alone_price=30)


if __name__ == "__main__":
    schafkopf.main()