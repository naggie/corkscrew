from random import shuffle
from itertools import cycle

# TODO: does game tell player filtered information, or can player enumerate entire game?
# TODO: consider if invisible cards allow 4-card brn rule (probably not, as invis cards could also manifest 4 in a row)
# TODO start swap feature

class IllegalMove(Exception): pass
class IveAlreadyWon(Exception): pass
class Deadlock(Exception): pass

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

        return self.shorthand_values[self.value] +' '+ self.shorthand_suits[self.suit]


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

    moves = 0

    # deadlock detection
    max_moves_per_player = 10000

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

        self.max_moves = self.max_moves_per_player * len(players)

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

        if self.ace_high and value == 1:
            value = 14

        if len(self.payload_pile) == 0:
            return

        # Magic card
        if cards[0] in self.magic_cards:
            return

        if current.value != self.lower_card:
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
            self.moves +=1

            if self.moves > self.max_moves:
                raise Deadlock('%s players',len(self.players))

            for card in cards:
                self.payload_pile.insert(0,card)

            if cards[0].value == self.burn_card:
                self.burn()

            if len(self.payload_pile) >= 4:
                same = 0
                for value in self.payload_pile[:4]:
                    if value == self.payload_pile[0].value:
                        same+=1
                if same == 4:
                    self.burn()


            if player.score() == 0:
                # TODO remove player, on_win
                # TODO continue the game until one player is left (loser)
                self.on_win(player)
                self.winner = player
                break

        return self

    def burn(self):
        while len(self.payload_pile):
            card = self.payload_pile.pop()
            self.discard_pile.append(card)


    def on_win(self,player): pass
    def on_lose(self): pass
    def on_join(self,player): pass
    def on_move(self,player,cards): pass
    def on_pickup(self,player,cards): pass
    def on_burn(self,player,cards): pass

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

    def on_burn(self,player,cards):
        print player,'burned',len(cards),'cards'

    def on_win(self,player):
        print player,'won'

players = [
    RandomLegalMovePlayer('Tania'),
    RandomLegalMovePlayer('Cal'),
    RandomLegalMovePlayer('Rasputin'),
    RandomLegalMovePlayer('Mitsy'),
]

PrintedGame(players).play_loop()

from sys import exit
exit(0)

scores = dict(
    Tania=0,
    Cal=0,
    Rasputin=0,
    Mitsy=0,
)

total_moves = 0
min_moves = 9999
max_moves = 0
deadlocks = 0

for x in range(3000):

    try:
        game = Game(players).play_loop()
    except Deadlock:
        deadlocks +=1

    print x, game.moves, 'moves'
    scores[game.winner.name] +=1

    total_moves += game.moves
    min_moves = min(min_moves,game.moves)
    max_moves = max(max_moves,game.moves)

print scores
print total_moves,'total moves'
print min_moves,'min moves'
print max_moves,'max moves'
print deadlocks,'deadlocks'
