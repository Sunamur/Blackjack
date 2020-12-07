import numpy as np
import random
import itertools


class Rules:
    """
    Base class for th erules, which will be used everywhere.
    """
    suits = ['♥', '♦', '♣', '♠']
    suits_txt = {'hearts': '♥', 'diamonds': '♦', 'clubs': '♣', 'spades': '♠'}
    nominals = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    no_of_decks = 2
    plastic_position = 20
    default_balance = 100
    minimal_bet = 5
    minimal_bet_step = 5


class Card(Rules):
    """
    Base class for cards
    """
    def __init__(self, suit, nominal):
        """
        suit: str, suit of the card
        nominal: str, nominal of the card

        """
        assert suit in self.suits
        self.suit = suit
        assert nominal in self.nominals
        self.nominal = nominal

    def __repr__(self):
        return f'{self.suit} {self.nominal}'

    def __str__(self):
        return f'{self.suit} {self.nominal}'

    def get_value(self):
        """
        Returns list of possible values of the card

        """
        if self.nominal in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
            return [int(self.nominal), ]
        elif self.nominal in ['J', 'Q', 'K']:
            return [10, ]
        elif self.nominal == 'A':
            return [1, 11]


class CardGroup(Rules):
    """
    Class of collection of cards
    Useful for representing the hands
    """

    def __init__(self, cards):
        """
        cards: list of Card objects
        """
        if cards:
            assert all([isinstance(card, Card) for card in cards])
            self.card_group = cards
        else:
            self.card_group = []

    def __repr__(self):
        return ", ".join([str(card) for card in self.card_group])

    def __add__(self, other):
        return CardGroup(self.card_group + other.card_group)

    def __len__(self):
        return len(self.card_group)

    def get_possible_values(self):
        """
        returns all possible values of the group (given that aces are ambiguous)
        """
        values = [card.get_value() for card in self.card_group]
        possible_values = [sum(x) for x in itertools.product(*values)]
        return possible_values

    def is_bust(self):
        """
        returns True if any possible value is above 21, False otherwise
        """
        possible_values = self.get_possible_values()
        return all([x > 21 for x in possible_values])

    def get_best_value(self):
        """
        returns the biggest value of all possible values, less or equal to 21
        """
        possible_values = self.get_possible_values()
        good_values = [x for x in possible_values if x < 22]
        if good_values:
            return max(good_values)
        else:
            return min(possible_values)


class Deck(Rules):
    """
    Class for deck, used for drawing
    """
    def __init__(self):
        self.deck = None

    def make_new_deck(self):
        """
        generates new deck based on the Rules class
        """
        deck_nominals = self.nominals * 4 * self.no_of_decks
        deck_suits = self.suits * 13 * self.no_of_decks

        random.shuffle(deck_nominals)
        random.shuffle(deck_suits)

        self.deck = iter([Card(x, y) for x, y in zip(deck_suits, deck_nominals)][:-self.plastic_position])

    def get_cards(self, num_cards):
        """
        num_cards: int, number of cards required for draw

        returns CardGroup of {num_cards} cards
        """
        if self.deck is None:
            self.make_new_deck()

        ret = []
        try:
            for _ in range(num_cards):
                ret.append(next(self.deck))
            return CardGroup(ret)
        except StopIteration:
            print('Plastic reached! Getting new deck.')
            self.make_new_deck()
            return self.get_cards(num_cards)


class Player(Rules):
    """
    Class to represent the player
    """
    def __init__(self, playerId, balance=None, ):
        """
        playerId: int, used to disambiguate players (would be used for Telegram implementation)
        balance: int, starting balance of the player; default None
        """
        if balance is None:
            self.balance = self.default_balance
        else:
            self.balance = balance
        self.playerId = playerId
        self.bet = 0


class StateHandler(Rules):
    """
    Class for states of the game and responding to player actions
    """
    def __init__(self, player):
        """
        player: Player
        """
        self.player = player
        self.flush_the_board()

    def __make_response(func):
        """
        decorator for compiling a response, which contains the current state of the game;
        """
        def decorator(*args, **kwargs):
            self = args[0]
            if self.player.balance+self.player.bet <= 0:
                raise BalanceIsZero

            message = func(*args, **kwargs)
            response = {
                'message': message,
                'dealer_cards': self.dealer_hand,
                'player_cards': self.player.hand,
                'bust': self.player.hand.is_bust(),
                'best_value': self.player.hand.get_best_value(),
                'is_standing': self.is_standing
            }
            return response
        return decorator

    def flush_the_board(self):
        """
        Clear the board, set all hands empty; used at the start of the round
        """
        self.dealer_hand = CardGroup([])
        self.player.hand = CardGroup([])
        self.is_standing = False

    @__make_response
    def ask_bet(self):
        """
        Checks if the balance is available, constructs the invitation for play
        """
        if self.player.balance >= self.minimal_bet:
            msg = f'Place your bet (min. {self.minimal_bet}, bet step {self.minimal_bet_step})'
        else:
            msg = 'Game over!'
        return msg

    def place_bet(self, bet_):
        """
        Sets the bet of the current game

        bet_: int, bet of the player
        """

        bet = int(bet_)
        if (bet > self.minimal_bet) and not bool(bet % self.minimal_bet_step):
            self.player.bet = bet
            self.player.balance -= bet
        else:
            raise ValueError

    @__make_response
    def initiate_the_board(self):
        """
        Provides dealer and the player with hands
        """
        if not ('deck' in dir(self)):
            self.deck = Deck()
        self.dealer_hand = self.deck.get_cards(1)
        self.player.hand = self.deck.get_cards(2)
        return 'Make your move'

    @__make_response
    def hit(self):
        """
        Process the hit of the player
        """

        self.player.hand += self.deck.get_cards(1)
        return 'Make your move'

    @__make_response
    def doubledown(self):
        """
        Process the doubledown of the player
        """

        if self.player.balance >= self.player.bet:
            bet = self.player.bet
            self.player.bet += bet
            self.player.balance -= bet
            self.player.hand += self.deck.get_cards(1)
            self.is_standing = True
            return 'Doubling down and standing'
        else:
            return 'Cant double down - not enough balance'

    @__make_response
    def draw_dealer(self):
        """
        Process the dealer draw at the end of the hitting
        """

        while max(self.dealer_hand.get_possible_values()) < 17:
            self.dealer_hand += self.deck.get_cards(1)
        return 'Dealer has finished drawing'

    @__make_response
    def stand(self):
        """
        Process the stand of the player
        """

        self.is_standing = True
        return 'Standing'

    @__make_response
    def finish_the_round(self):
        """
        Processing the results of the round
        """

        if self.player.hand.is_bust():
            status = 'lost'
            message = 'You lost (busted)'
        elif self.dealer_hand.is_bust():
            status = 'won'
            message = 'You won (dealer busted)'
        elif self.player.hand.get_best_value() > self.dealer_hand.get_best_value():
            status = 'won'
            message = 'You won (on value)'
        elif self.player.hand.get_best_value() == self.dealer_hand.get_best_value():
            status = 'push'
            message = 'Push (bet returned)'
        else:
            status = 'lost'
            message = 'You lost (on value)'

        if status == 'won':
            self.player.balance += self.player.bet*2
        elif status == 'push':
            self.player.balance += self.player.bet
        self.player.bet = 0

        return message


class BlackjackCLI(Rules):
    """
    CLI interface for the game; accepts the actions of the player and renders repsonses
    """

    def __init__(self):
        """
        Initiates the interface
        """
        # There is always only one player, unlike the Telegram case.
        self.player = Player(1)
        self.state = StateHandler(self.player)

    def render_response(self, response, options_list=[]):
        """
        Collects and returns the string response to the player

        response: dict, response as given by the StateHanfler object
        options_list: list, possible reactions of the player
        """

        screen_width = 80
        return_strings = []
        return_strings.append('\n\n')
        return_strings.append(response['message'].ljust(screen_width-len('Dealer hand'), ' ') + 'Dealer hand')
        dealer_hand_line = f'{str(response["dealer_cards"])} ({response["dealer_cards"].get_best_value()})'.rjust(screen_width, ' ') \
            if len(response["dealer_cards"]) else '---'.rjust(screen_width, ' ')
        return_strings.append(dealer_hand_line)
        return_strings.append(f'Balance: {self.player.balance}'.ljust(screen_width, ' '))
        return_strings.append('Player hand'.rjust(screen_width, ' '))
        options = '/'.join(options_list)
        player_hand_line = f'{str(response["player_cards"])} ({response["player_cards"].get_best_value()})' if len(response["player_cards"]) else '---'
        bet_line = f'Your bet: {self.player.bet}' if self.player.bet else ''
        return_strings.append(bet_line.ljust(screen_width-len(player_hand_line), ' ')+player_hand_line)
        return_strings.append(options.ljust(screen_width))

        return '\n'.join(return_strings)+'\n'

    def play_round(self):
        """
        Handles the flow of the round.
        """

        bet_invalid = True
        self.state.flush_the_board()
        while bet_invalid:
            try:
                bet = input(self.render_response(self.state.ask_bet(), options_list=['Input your bet']))
                self.state.place_bet(bet)
                bet_invalid = False
            except ValueError:
                pass

        response = self.state.initiate_the_board()
        round_is_active = True
        while round_is_active:
            if response['player_cards'].is_bust():
                round_is_active = False
                continue  # busted, finish the round
            if response['is_standing']:
                round_is_active = False
                continue  # game is done, dealer draw and finish the round
            options_list = ['(H)it', '(S)tand', '(D)oubledown']
            player_input = input(self.render_response(response, options_list=options_list)).upper()
            if not (player_input in ['H', 'S', 'D']):
                continue
            if player_input == 'H':
                response = self.state.hit()
                continue
            elif player_input == 'D':
                response = self.state.doubledown()
                continue
            elif player_input == 'S':
                response = self.state.stand()
                continue
        response = self.state.draw_dealer()
        self.render_response(response, [])
        replay = input(self.render_response(self.state.finish_the_round(), ['(A)gain', '(S)top'])).upper()
        if replay == 'A':
            self.play_round()
        elif replay == 'S':
            print('Bye!')


class BalanceIsZero(Exception):
    """
    Exception raised when the game is over

    """

    def __init__(self, message="Your balance is zero, go home!"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


if __name__ == '__main__':
    game = BlackjackCLI()
    game.play_round()
