from random import shuffle
from itertools import cycle

class PlayingCard():
    values = [
        'Joker',
        'Ace',
        'Two',
        'Three',
        'Four',
        'Five',
        'Six',
        'Seven',
        'Eight',
        'Nine',
        'Ten',
        'Jack',
        'Queen',
        'King',
    ]

    shorthand_values = [
        'JOK','A','1','2','3','4','5','6',
        '7','8','9','10','J','Q','K','A',
    ]

    # unicode, terminal, yo!
    # TODO UNICODE symbols
    shorthand_suits = [
        u'\u2660', # spade
        u'\u2663', # club
        u'\033[31m\u2666\033[0m', # diamond
        u'\033[31m\u2665\033[0m', # heart
    ]

    suits = [
        'Spades',
        'Clubs',
        'Diamonds',
        'Hearts',
    ]


    def __init__(self,value,suit):
        # 14 is Ace high, 1 is Ace low
        if value >=0 and value <= 13:
            self.value = value
        else:
            raise ValueError('Value must be 0-13, 0 is joker')

        if suit >=0 and suit <= 3:
            self.suit = suit
        else:
            raise ValueError('Suit is 0-3')


    def __str__(self):
        if self.value == 0:
            return self.values[0]

        return self.values[self.value] + ' of ' + self.suits[self.suit]

    def shorthand(self):
        if self.value == 0:
            return self.shorthand_values[0]

        return self.shorthand_suits[self.suit] +' '+ self.shorthand_values[self.value]


class Deck():
    cards = list()

    def __init__(self):
        for suit in range(4):
            for value in range(14):
                card = PlayingCard(value,suit)
                self.cards.append(card)

    def shuffle(self):
        shuffle(self.cards)
        return self


class Player():
    bottom = list()
    top = list()
    hand = list()

    def __init__(self,name):
        self.name = name

    def join_game(self,game,cards):
        if len(cards) < 9:
            raise ValueError('New players require 9 cards')

        self.bottom = cards[0:3]
        self.top = cards[3:6]
        self.hand = cards[6:9]
        self.game = game

    def make_move(self):
        raise NotImplementedError('Define this method')

    def pickup_payload(self,cards):
        self.hand.append(cards)

    def score(self):
        '''Lower is better, zero wins.'''
        return len(self.bottom + self.top + self.hand)


class RandomLegalMovePlayer(Player):
    def make_move(self):
        shuffle(self.hand)

        for i in range(len(self.hand)):
            try:
                game.check_move(cards[i])
                return cards.pop[i]
            except IllegalMove:
                continue

        return None

        # ...etc

class BestCardsPlayer(Player): pass
class CalPlayer(Player): pass

class Game():
    burn_pile = list()
    payload_pile = list()
    supply_pile = list()

    players = list()

    reset_card = 2
    invisible_card = 3
    lower_card = 7
    burn_card = 10
    reverse_card = 0 # also invisible

    # can always go
    magic_cards = set([
            reset_card,
            invisible_card,
            lower_card,
            burn_card,
            reverse_card,
    ])

    def __init__(self,players):
        self.supply_pile = Deck().shuffle().cards

        self.players = players

        for player in players:
            cards = list()
            for i in range(9):
                card = self.supply_pile.pop()
                cards.append(card)

            player.join_game(self,cards)

    def check_move(self,cards):
        current = self.effective_current_card()
        # nothing (implies pickup)
        if len(cards) == 0:
            return

        # Check for suit coherence
        for card in cards:
            if cards[0].suit != card.suit:
                raise IllegalMove('Cards must be of coherent suit')

        if len(self.payload_pile) == 0:
            return

        # Magic card
        if card[0] in self.magic_cards:
            return

        if current.value != self.lower_card:
            if card[0].value < current.value:
                raise IllegalMove('Card value too low')
        elif card[0].value > self.lower_card:
                raise IllegalMove('Card value too high')

    def effective_current_card(self):
        '''Ignoring invisible cards...'''
        if len(self.payload_pile):
            for card in self.payload_pile:
                if card not in (self.invisible_card,self.reverse_card):
                    return card

            # Only invisible cards on table
            return None
        else:
            # No cards on table
            return None

    def play_loop():
        for player in cycle(self.players):
            cards = player.make_move()

            if len(cards) == 0:
                player.pickup_payload(self.payload_pile)
                continue

            self.check_move(cards)

            if player.score() == 0:
                break


players = [
    RandomLegalMovePlayer('Tania'),
    RandomLegalMovePlayer('Cal'),
    RandomLegalMovePlayer('Rasputin'),

]

Game(players)
