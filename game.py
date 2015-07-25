from random import shuffle
from itertools import cycle

# TODO: does game tell player filtered information, or can player enumerate entire game?

class IllegalMove(Exception): pass
class IveAlreadyWon(Exception): pass

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
        'JOK','A','2','3','4','5','6',
        '7','8','9','10','J','Q','K',
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

    def __str__(self):
        return self.name

    def join_game(self,game,cards):
        if len(cards) < 9:
            raise ValueError('New players require 9 cards')

        self.bottom = cards[0:3]
        self.top = cards[3:6]
        self.hand = cards[6:9]
        self.game = game

    def score(self):
        '''Lower is better, zero wins.'''
        return len(self.bottom + self.top + self.hand)

    def pickup_payload(self,cards):
        while len(cards):
            card = cards.pop()
            self.hand.append(card)

    def make_move(self,effective_card):
        if len(self.hand):
            return self.play_hand(effective_card)
        if len(self.top):
            return self.play_top(effective_card)
        if len(self.bottom):
            return self.play_bottom(effective_card)
        else:
            raise IveAlreadyWon()


    def play_hand(self,effective_card):
        raise NotImplementedError('Define this method')

    def play_top(self,effective_card):
        '''The top set of cards -- bear in bind everyone can see them. Assumes hand is exhausted'''
        raise NotImplementedError('Define this method')

    def play_bottom(self,effective_card):
        '''Play a random bottom card, assuming top and hand are exhausted'''
        return [self.bottom.pop()]



class RandomLegalMovePlayer(Player):
    def play_hand(self,effective_card):
        return self._take_random_legal_card(self.hand)

    def play_top(self,effective_card):
        return self._take_random_legal_card(self.top)

    def _take_random_legal_card(self,cards):
        shuffle(cards)

        for i in range(len(cards)):
            try:
                self.game.check_move([cards[i]])
                return [cards.pop(i)]
            except IllegalMove:
                continue

        return [] # pickup

class BestCardsPlayer(Player): pass
class CalPlayer(Player): pass

class Game():
    discard_pile = list()
    payload_pile = list()
    supply_pile = list()

    players = list()

    reset_card = 2
    invisible_card = 3
    lower_card = 7
    burn_card = 10
    reverse_card = 0 # also invisible

    # TODO: could be both option: None
    ace_high = True

    # can always go
    magic_cards = set([
            reset_card,
            invisible_card,
            lower_card,
            burn_card,
            reverse_card,
    ])

    winner = None
    loser = None

    def __init__(self,players):
        self.supply_pile = Deck().shuffle().cards

        self.players = players

        for player in players:
            cards = list()
            for i in range(9):
                card = self.supply_pile.pop()
                cards.append(card)

            player.join_game(self,cards)
            self.on_join(player)

    def check_move(self,cards):
        current = self.effective_current_card()

        # nothing (implies pickup)
        if len(cards) == 0:
            return

        value = cards[0].value

        # Check for suit coherence
        for card in cards:
            if cards[0].suit != card.suit:
                raise IllegalMove('Cards must be of coherent suit')

        if self.ace_high:
            value = 14

        if len(self.payload_pile) == 0:
            return

        # Magic card
        if cards[0] in self.magic_cards:
            return

        if value != self.lower_card:
            if value < current.value:
                raise IllegalMove('Card value too low')
        elif value > self.lower_card:
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

    def play_loop(self):
        # TODO deal with reverse
        for player in cycle(self.players):
            effective_card = self.effective_current_card()
            cards = player.make_move(effective_card)

            if len(cards) == 0:
                self.on_pickup(player,self.payload_pile)
                player.pickup_payload(self.payload_pile)
                continue

            try:
                self.check_move(cards)
            except IllegalMove:
                self.on_pickup(player,self.payload_pile)
                player.pickup_payload(self.payload_pile)

            self.on_move(player,cards)

            for card in cards:
                self.payload_pile.insert(0,card)

            if cards[0].value == self.burn_card:
                while len(self.payload_pile):
                    card = self.payload_pile.pop()
                    self.discard_pile.append(card)

            if player.score() == 0:
                # TODO remove player, on_win
                # TODO continue the game until one player is left (loser)
                self.on_win(player)
                self.winner = player
                break

        return self


    def on_win(self,player): pass
    def on_lose(self): pass
    def on_join(self,player): pass
    def on_move(self,player,cards): pass
    def on_pickup(self,player,cards): pass

class PrintedGame(Game):
    def on_join(self,player):
        print player.__class__.__name__,player,'joined'

    def on_move(self,player,cards):
        print player,'played',
        print ' ' * (20-len(player.name)),
        print ' '.join([card.shorthand() for card in cards])
        #print ' '.join([str(card) for card in cards])

    def on_pickup(self,player,cards):
        print player,'picked up',len(cards),'cards'

    def on_win(self,player):
        print player,'won'

players = [
    RandomLegalMovePlayer('Tania'),
    RandomLegalMovePlayer('Cal'),
    RandomLegalMovePlayer('Rasputin'),
]

# PrintedGame(players).play_loop()

scores = dict(
    Tania=0,
    Cal=0,
    Rasputin=0,
)

for x in range(1000):
    print x
    game = Game(players).play_loop()
    scores[game.winner.name] +=1

print scores
