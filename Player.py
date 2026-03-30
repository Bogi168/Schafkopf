from Renderer import Renderer
from Cards import Card
from roolbook import is_move_legal

class Player:
    def __init__(self, player_name):
        self.player_name = player_name
        self.player_cards = []
        self.collected_cards = []
        self.bool_beginner = False

    def __repr__(self):
        return self.player_name

    def bool_valid_number(self, decision) -> bool:
        return decision in ("1", "2", "3", "4", "5", "6", "7", "8") and int(decision) <= len(self.player_cards)

    def decision(self, renderer: Renderer, lead_card: Card, played_cards: list, trumps: list):
        print(self.player_cards)
        index_decision = renderer.ask_player_decision(self.player_name, player_cards=self.player_cards)
        while not self.bool_valid_number(index_decision):
            index_decision = renderer.reask_player_decision(self.player_name, player_cards=self.player_cards)
            if self.bool_valid_number(index_decision):
                break
        decision = self.player_cards[int(index_decision) - 1]
        legal = is_move_legal(decision=decision, player_cards=self.player_cards, lead_card=lead_card, trumps=trumps)
        while not legal:
            index_decision = renderer.reask_player_decision(self.player_name, player_cards=self.player_cards)
            decision = self.player_cards[int(index_decision) - 1]
            legal = is_move_legal(decision=decision,player_cards=self.player_cards, lead_card=lead_card, trumps=trumps)
        played_cards.append(decision)
        self.player_cards.remove(decision)