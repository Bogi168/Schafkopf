# Schafkopf

A terminal implementation of Schafkopf, the traditional Bavarian card game, written in Python. You play against three bots, and your money balance is tracked across rounds.

The focus of this project is the rule engine: a clean, testable architecture that models the rules of Schafkopf, including its many game modes and edge cases.

## Game modes

- Sauspiel: The chooser calls an Ace (Sau). Whoever holds it becomes the secret partner.
- Hochzeit: A player holding exactly one trump offers it to find a partner.
- Wenz: Only the four Unter are trump. The chooser plays alone.
- Solo: Ober, Unter and a chosen suit are trump. The chooser plays alone.
- Wenz Tout / Solo Tout: Like Wenz / Solo, but the chooser must win every trick.
- Ramsch: Played when nobody chooses a game. The player with the most points loses.

Scoring includes doubling the stakes (Legen), shooting and shooting back (Schießen / Zurückschießen), Schneider and runners (Laufende).

## Running the game

From the project root:

python3 -m system.run

## Running the tests

python3 -m pytest tests/

## Architecture

- Game modes as subclasses: Each game mode is a subclass of the abstract Game class and registers itself with a GameRegistry via a decorator. Each mode brings its own components for trick rules, team building and scoring, instead of one central class handling everything with if/else chains.
- Separated responsibilities: The round flow lives in RoundManager, output formatting in GameRenderer. Dependencies are passed in via the constructor, which keeps the game logic testable in isolation.
- Renderer abstraction: All input and output goes through an abstract Renderer. The current implementation is a ConsoleRenderer. The game logic itself never talks to the terminal directly.

## Project layout

- card_classes: Cards, deck, card power calculation
- game_classes: Game base class, game modes, rounds, teams, runners
- input_validators: Validation of legal moves and game choices
- money_handling: Winner selection, game value calculation, money distribution
- player_classes: Player, Bot, Team
- schafkopf_classes: Main game loop
- system: Renderer, entry point, display texts, custom exceptions
- tests: pytest suite

## Limitations

Whether the bots want to play or not and the game, they want to play, has to be selected manually at the moment.
The bots currently play a random legal card. This repository focuses on the rules and the architecture, not on bot strategy.

A separate version with a pygame GUI and stronger bot heuristics, built with Claude Code on top of this codebase, can be found here: https://github.com/Bogi168/GUI_Schafkopf
