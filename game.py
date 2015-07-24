from random import shuffle

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

class Game():
    self.burn_pile = list()
    self.payload_pile = list()
    self.supply_pile = list()

    self.players = list()

    def __init__(self,players):
        self.supply_pile = Deck().shuffle().cards

        self.player = players

