from random import shuffle
class Deck:
    def  __init__(self) -> None:
        self.suits = ['h', 'd', 'c', 's']
        self.values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'j', 'q', 'k', 'a']
        self.deck = [(value, suit) for suit in self.suits for value in self.values]
        
    def shuffle(self):
        shuffle(self.deck)
        return self.deck