import numpy as np
import random
import itertools



class Rules:
    suits = ['♥','♦','♣','♠']
    suits_txt = {'hearts':'♥','diamonds':'♦','clubs':'♣','spades':'♠'}
    nominals = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    no_of_decks=2
    plastic_position = 20
    default_balance = 100



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
        if self.nominal in ['2','3','4','5','6','7','8','9','10',]:
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

    def __add__(self, other):
        return self.card_group + other.card_group


    def get_possible_values(self):
        values = [card.get_value() for card in self.card_group]
        print(values)
        possible_values = [sum(x) for x in itertools.product(*values)]
        return possible_values






class Deck(Rules):

    def __init__(self):
        self.deck = None
        
    
    def make_new_deck(self):
        deck_nominals = self.nominals * 4 * self.no_of_decks
        deck_suits = self.suits * 13 * self.no_of_decks

        random.shuffle(deck_nominals)
        random.shuffle(deck_suits)

        self.deck = iter([Card(x,y) for x,y in zip(deck_suits, deck_nominals)][:-self.plastic_position])

    def get_cards(self, num_cards):
        if self.deck is None:
            self.make_new_deck()

        ret = []
        try:
            for i in range(num_cards):
                ret.append(next(self.deck))
            return ret
        except StopIteration:
            print('Plastic reached! Getting new deck.')
            self.make_new_deck()
            return self.get_cards(num_cards)





class Player(Rules):
    def __init__(self, balance=None):
        if balance is None:
            self.balance = self.default_balance
        else:
            self.balance = balance

    


class GameSession:
    def __init__(self, player):
        self.player = player
    
    



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
    print(f'My hand is of these possible values: {hand.get_possible_values()}')
    
    deck = Deck()
    print(deck.get_cards(2))
    print(deck.get_cards(50))
    print(deck.get_cards(2))
    