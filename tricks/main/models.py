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
        ('11', 'Jack'),
        ('12', 'Queen'),
        ('13', 'King'),
        ('14', 'Ace'),
    )

    suit = models.CharField(max_length=10, choices=SUIT_CHOICES)
    rank = models.CharField(max_length=5, choices=RANK_CHOICES)
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
    def is_better(self, winning_card, trump_suit):
        if self.suit == winning_card.suit:
            return int(self.rank) > int(winning_card.rank)
        elif self.suit == trump_suit:
            return True
        else:
            return False
        
class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hand = models.ManyToManyField(Card, blank=True, related_name='hand')
    bet_pos = models.SmallIntegerField(default=0, blank=True, null=True)
    play_pos = models.SmallIntegerField(default=0, blank=True, null=True)
    cur_card = models.ForeignKey(Card, blank=True, null=True,
                                      related_name='cur_card', on_delete=models.CASCADE)
    bet = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    def __str__(self):
        return f'{self.user}'
    
    def __repr__(self):
        return f'{self.user}'
    
    def bet_range(self, cur_round):
        players = cur_round.players.all().order_by('bet_pos')
        bet_range = [num for num in range(cur_round.cards_dealt + 1)]
        if self == players.last():
            cant_bet = cur_round.num - cur_round.bet_sum
            if cant_bet in bet_range:
                bet_range.remove(cant_bet)
                return bet_range
        return bet_range
        
    
    def set_bet(self, bet:int, cur_round):
        self.bet = bet
        cur_round.bet_sum += bet
        cur_round.save()
        self.save()
    
    def playable_cards(self, cur_round):
        playable_cards = []
        for card in self.hand.all():
            if not cur_round.trick:
                playable_cards.append(card)
            elif card.suit == cur_round.trick.suit:
                playable_cards.append(card)
            elif card.suit == cur_round.trump.suit:
                playable_cards.append(card)
        if not playable_cards:
            return self.hand.all()
        return playable_cards
    
    def play_card(self, card, cur_round):
        self.cur_card = card
        self.hand.remove(card)
        self.save()
        cur_round.table.add(card)
        if not cur_round.trick:
            cur_round.trick = card
            cur_round.save()
    
    def update_wins(self):
        self.wins += 1
        self.save()
    
    def calc_score(self):
        if self.bet == self.wins:
            self.score += 10 + self.bet
        self.save()

class Round(models.Model):
    num = models.IntegerField()
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    dealer = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='dealer')
    deck = models.ManyToManyField(Card, blank=True, related_name='deck')
    table = models.ManyToManyField(Card, blank=True, related_name='table')
    trump = models.ForeignKey(Card, on_delete=models.CASCADE, blank=True, null=True,
                              related_name='trump')
    trick = models.ForeignKey(Card, blank=True, null=True, on_delete=models.CASCADE,
                                   related_name='trick')
    bet_sum = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    @property
    def players(self):
        return self.game.players.all()
    
    @property
    def cards_dealt(self):
        if self.deck.count() > 0:
            return self.game.cur_round.num
        return 0
    
    def __str__(self):
        return f'Round {self.num}'
    
    def __repr__(self):
        return f'Round {self.num}'
    
    def deal_cards(self):
        deck = [Card(suit=c_suit, rank=c_rank)
                     for c_suit in ['s', 'h', 'c', 'd']
                     for c_rank in range(2, 15)]
        shuffle(deck)
        deck = Card.objects.bulk_create(deck)
        
        players = self.players.all()
        for player in players:
            player.hand.set([deck.pop() for _ in range(self.num)], clear=True)
        self.trump = deck.pop()
        self.deck.set(deck, clear=True)
        self.save()
    
    def start_new_trick(self):
        # assumes trick is complete
        winner = self.get_trick_winner()
        winner.update_wins()
        self.reset_cur_cards()
        self.reset_table()
        self.reset_trick()
        self.update_play_order(winner)
    
    def reset_cur_cards(self):
        players = self.players.all()
        for player in players:
            player.cur_card = None
            player.save()
            
    def reset_table(self):
        self.table.clear()
        self.save()
    
    def reset_trick(self):
        self.trick = None
        self.save()
    
    def update_play_order(self, starting_player):
        players = self.players.all().order_by('play_pos')
        players = deque(players)
        start_idx = players.index(starting_player)
        players.rotate(-start_idx)
        play_pos = 0
        for player in players:
            player.play_pos = play_pos
            player.save()
            play_pos += 1
    
    def check_trick_complete(self):
        """checks if the trick is complete

        Returns:
            bool: True if trick is complete, False otherwise
        """
        return len(self.table.all()) == len(self.players.all())
    
    def get_trick_winner(self):
        """returns the player who won the trick

        Returns:
            Player: player who won the trick
        """
        players = self.players.all().order_by('play_pos')
        winner = players.first()
        winning_card = winner.cur_card
        for player in players:
            if player.cur_card.is_better(winning_card, self.trump.suit):
                winner = player
                winning_card = player.cur_card
        return winner
        
    def calc_scores(self):
        players = self.players
        for player in players:
            player.calc_score()

# TODO: delete bet_turn field, managing bet_trun in views            
class Game(models.Model):
    players = models.ManyToManyField(Player, blank=True)
    num_of_rounds = models.IntegerField(default=7)
    rounds = models.ManyToManyField(Round, blank=True, related_name='cur_rounds')
    bet_turn = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    @property
    def cur_round(self):
        rounds = self.rounds.all()
        if rounds.count() > 0:
            return rounds.last()
    
    @property
    def in_play(self):
        if self.rounds.count() > 0:
            return True
    
    def __str__(self):
        return f'Game {self.id}'
    
    def __repr__(self):
        return f'Game {self.id}'

    def add_player(self, player:Player):
        if self.players.count() > 0:
            last_player = self.players.last()
            player.bet_pos = last_player.bet_pos + 1
            player.play_pos = last_player.play_pos + 1
            player.save()
        self.players.add(player)
        self.save()
    
    def rotate_dealer(self):
        players = deque(self.players.all().order_by('bet_pos'))
        players.rotate(-1)
        pos = 0
        for player in players:
            player.bet_pos = pos
            player.play_pos = pos
            player.save()
            pos += 1
        players = self.players.all()
        return players
    
    def check_round_complete(self):
        """checks if the round is complete
        
        Returns:
            bool: True if round is complete, False otherwise
        """
        players = self.players.all()
        hand_cards_left = 0
        if self.cur_round.num == 1:
            True
        for player in players:
            hand_cards_left += player.hand.count()
            if hand_cards_left > 0:
                return False
        return True
    
    def reset_bets_and_wins(self):
        players = self.players.all()
        for player in players:
            player.bet = None
            player.wins = 0
            player.save()

    def end_round(self):
        cur_round = self.cur_round
        cur_round.calc_scores()
        self.reset_bets_and_wins()
    
    def start_new_round(self):
        """_summary_
        """
        if self.rounds.count() != 0:
            cur_round = self.cur_round
            players = self.rotate_dealer()
            round_num = cur_round.num - 1
        else:
            players = self.players.all()
            round_num = self.num_of_rounds
        dealer = players.get(bet_pos=0)
        cur_round = Round.objects.create(game = self,
                                         num=round_num, dealer=dealer)
        cur_round.deal_cards()
        self.rounds.add(cur_round)
        self.save()
        return cur_round
    
    # TODO: move to views        
    def end_game(self):
        winners = []
        players = self.players.all().order_by('score')
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