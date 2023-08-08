from django.db import models
from django.contrib.auth.models import User
from collections import deque
from random import shuffle

class Card(models.Model):
    SUIT_CHOICES = (
        ('h', 'Hearts'),
        ('d', 'Diamonds'),
        ('c', 'Clubs'),
        ('s', 'Spades'),
    )

    RANK_CHOICES = (
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('j', 'Jack'),
        ('q', 'Queen'),
        ('k', 'King'),
        ('a', 'Ace'),
    )

    suit = models.CharField(max_length=10, choices=SUIT_CHOICES)
    rank = models.CharField(max_length=5, choices=RANK_CHOICES)
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
    def compare_rank(self, winning_card, trump_suit):
        if self.suit == winning_card.suit:
            return self.rank > winning_card.rank
        elif self.suit == trump_suit:
            return True
        else:
            return False
        
class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hand = models.ManyToManyField(Card, blank=True, null=True)
    trick = models.ManyToManyField(Card, blank=True, null=True)
    bet = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.user}'
    
    def __repr__(self):
        return f'{self.user}'
    
    def bet_range(self, cur_round):
        players = deque(cur_round.players.all())
        if self == players[-1]:
            return range(cur_round.cards_dealt - cur_round.bet_sum,
                         cur_round.cards_dealt + 1)
        return range(0, cur_round.cards_dealt + 1)
        
    
    def set_bet(self, bet:int, cur_round):
        if self.invalid_bet(bet, cur_round):
            raise ValueError('Invalid bet.')
        self.bet = bet
        cur_round.bet_sum += bet
        self.save()
        
    def invalid_bet(self, bet, cur_round):
        players = deque(cur_round.players.all())
        if bet == None:
            return True
        if self == players[-1] and bet == (cur_round.cards_dealt - cur_round.bet_sum):
            return True
        return False
    
    def invalid_card(self, card, cur_round) -> bool:
        hand = self.hand.all()
        if card not in hand:
            return True
        
        playable_cards = [card for card in self.hand if card.suit == cur_round.trick.suit]
        
        if len(playable_cards) == 0:
            playable_cards = self.hand
        else:
            playable_cards += [card for card in self.hand
                               if card.suit == cur_round.trump_suit]
        if card in playable_cards:
            return False
        return True
    
    def play_card(self, card, cur_round):
        if self.invalid_card(card, cur_round):
            raise ValueError('Invalid card.')
        self.hand.remove(card)
        self.trick.add(card)
        self.save()
        cur_round.table.add(card)
        if not cur_round.trick:
            cur_round.trick = card
        cur_round.save()
    
    def calc_score(self):
        if self.bet == self.wins:
            self.score += 10 + self.bet
        self.save()

class Round(models.Model):
    num = models.IntegerField()
    players = models.ManyToManyField(Player)
    dealer = models.ForeignKey(Player, on_delete=models.CASCADE)
    deck = models.ManyToManyField(Card, blank=True, null=True)
    table = models.ManyToManyField(Card, blank=True, null=True)
    trump = models.ForeignKey(Card, on_delete=models.CASCADE, blank=True, null=True)
    trick = models.ManyToManyField(Card, blank=True, null=True)
    cards_dealt = models.IntegerField(default=0)
    bet_sum = models.IntegerField(default=0)
    
    def __str__(self):
        return f'Round {self.num}'
    
    def __repr__(self):
        return f'Round {self.num}'
    
    def add_player(self, player:Player):
        self.players.add(player)
        self.save()
    
    def deal_cards(self):
        deck = [Card(suit, rank)
                     for suit in ['s', 'h', 'c', 'd']
                     for rank in range(2, 15)]
        shuffle(deck)
        self.deck.add(*deck)
        
        players = self.players.all()
        self.cards_dealt = self.num
        for player in players:
            player.hand.add([deck.pop() for _ in range(self.num)])
        self.trump = deck.pop()
        self.save()
        
    def rotate_players(self, players, starting_player):
        players = deque(players.all())
        start_idx = players.index(starting_player)
        players.rotate(-start_idx)
        return players
    
    def check_trick_complete(self):
        if len(self.table.all()) == len(self.players.all()):
            trick_winner = self.get_trick_winner()
            trick_winner.wins += 1
            trick_winner.save()
            self.players.set(self.rotate_players(self.players, trick_winner),
                             clear=True)
            self.save()
            return True
        return False
    
    def get_trick_winner(self):
        """returns the player who won the trick, while
        also clearing the table and trick fields for each
        player

        Returns:
            Player: player who won the trick
        """
        winner = None
        players = self.players
        for player in players:
            trick = player.trick.first()
            if not winner:
                trick = player.trick.first()
            elif trick.compare_rank(winner.trick, self.trump.suit):
                winner = player
            player.trick = None
            player.save()
        return winner
        
    def calc_scores(self):
        players = self.players
        for player in players:
            player.calc_score()
            
class Game(models.Model):
    players = models.ManyToManyField(Player)
    num_of_rounds = models.IntegerField(default=7)
    rounds = models.ManyToManyField(Round, blank=True, null=True)
    bet_turn = models.IntegerField(default=0)
    
    @property
    def cur_round(self):
        rounds = deque(self.rounds.all())
        if len(rounds) > 0:
            return rounds[-1]
    
    @property
    def in_play(self):
        if len(self.rounds.all()) > 0:
            return True
    
    def __str__(self):
        return f'Game {self.id}'
    
    def __repr__(self):
        return f'Game {self.id}'
    
    def rotate_dealer(self):
        players = deque(self.players.all())
        players.rotate(-1)
        self.players.set(*players, clear=True)
        self.save()
    
    def check_round_complete(self):
        """checks if the round is complete
        
        Returns:
            bool: True if round is complete, False otherwise
        """
        players = self.players
        hand_cards_left = 0
        for player in players:
            hand_cards_left += len(player.hand.all())
            if hand_cards_left > 0:
                return False
        return True
    
    def start_new_round(self):
        """_summary_
        """
        cur_round = self.cur_round
        cur_round.calc_scores()
        players = self.rotate_dealer()
        cur_round = Round.objects.create(num=cur_round.num - 1,
                                            players = players,
                                            dealer=players.first(),)
        cur_round.deal_cards()
        self.rounds.add(cur_round)
        self.save()
    
    # TODO: move to views        
    def end_game(self):
        winners = []
        players = self.players
        for player in players:
            if not winners:
                winners.append(player)
            elif player.score == winners[0].score:
                winners.append(player)
            elif player.score > winners[0].score:
                winners = [player,]
        for winner in winners:
            print(f'{winner} wins!')
        return winners