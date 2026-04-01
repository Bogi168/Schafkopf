from Renderer import Renderer
from Cards import Card
from roolbook import is_move_legal
from  Game import Game

class Player:
    def __init__(self, player_name):
        self.player_name = player_name
        self.player_cards = []
        self.collected_cards = []

    def __repr__(self):
        return self.player_name

    def choose_game_decision(self):
        pass

    def bool_valid_card_number(self, index_decision) -> bool:
        return index_decision in ("1", "2", "3", "4", "5", "6", "7", "8") and int(index_decision) <= len(self.player_cards)

    def card_decision(self, game_mode: Game, renderer: Renderer, lead_card: Card, played_cards: list, trumps: list, call_sau: Card):
        print(self.player_cards)
        index_decision = renderer.ask_player_card_decision(player_name=self.player_name, player_cards=self.player_cards)
        while not self.bool_valid_card_number(index_decision=index_decision):
            index_decision = renderer.reask_player_card_decision(player_name=self.player_name, player_cards=self.player_cards)
            if self.bool_valid_card_number(index_decision=index_decision):
                break
        decision = self.player_cards[int(index_decision) - 1]
        legal = is_move_legal(game_mode=game_mode, decision=decision, player_cards=self.player_cards, lead_card=lead_card, trumps=trumps, call_sau=call_sau)
        while not legal:
            index_decision = renderer.reask_player_card_decision(self.player_name, player_cards=self.player_cards)
            if not self.bool_valid_card_number(index_decision):
                legal = False
            else:
                decision = self.player_cards[int(index_decision) - 1]
                legal = is_move_legal(game_mode=game_mode, decision=decision, player_cards=self.player_cards, lead_card=lead_card, trumps=trumps, call_sau=call_sau)
        played_cards.append(decision)
        self.player_cards.remove(decision)