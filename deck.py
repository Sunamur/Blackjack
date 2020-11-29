import numpy as np
import random




class Rules:
    suits = ['♥','♦','♣','♠']
    suits_txt = {'hearts':'♥','diamonds':'♦','clubs':'♣','spades':'♠'}
    nominals = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']



class Card(Rules):

    def __init__(self, suit, nominal):
        assert suit in self.suits
        self.suit = suit
        assert nominal in self.nominals
        self.nominal = nominal


    def __repr__(self):
        return f'{self.suit} {self.nominal}'

    def __str__(self):
        return f'{self.suit} {self.nominal}'


    def get_value(self):
        if self.nominal in ['2','3','4','5','6','7','8','9',]:
            return [int(self.nominal),]
        elif self.nominal in ['J','Q','K']:
            return [10,]
        elif self.nominal=='A':
            return [1,11]






class CardGroup(Rules):

    def __init__(self, *cards):
        assert all([isinstance(card, Card) for card in cards])
        self.card_group = cards

    def __repr__(self):
        return f'A group of {len(self.card_group)} cards: {", ".join([str(card) for card in self.card_group])}'


class Deck:
    pass

if __name__=='__main__':
    card1 = Card(Rules.suits_txt['spades'], '10')
    card2 = Card(Rules.suits_txt['hearts'], '2')
    card3 = Card(Rules.suits_txt['clubs'], 'K')
    print('Made some cards:')
    print(card1)
    print(card2)
    print(card3)

    hand = CardGroup(card1, card2, card3)
    print(f'now my hand is {hand}')
    