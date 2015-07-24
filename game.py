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
        u's',
        u'c',
        u'\033[31md\033[0m',
        u'\033[31mh\033[0m',
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

    magic_cards = [2,3,7,10,0]

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
        if len(cards) == 0:
            return

        # Check for suit coherence
        for card in cards:
            if cards[0].suit != card.suit
                raise IllegalMove('Cards must be of coherent suit')


        raise IllegalMove('Cannot lay ' + ','.join(cards) +' on '+ self.current_card())

    def play_loop():
        for player in cycle(self.players):
            cards = player.make_move()

            if len(cards) == 0:
                player.pickup_payload(self.payload_pile)
                continue

            self.check_move(cards):

    def current_card(self):
        if len(self.payload_pile):
            return self.payload_pile[0]
        else:
            return None

players = [
    RandomLegalMovePlayer('Tania'),
    RandomLegalMovePlayer('Cal'),
    RandomLegalMovePlayer('Rasputin'),

]

Game(players)
