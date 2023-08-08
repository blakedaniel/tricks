from django.db import models
from django.contrib.auth.models import User
from random import sample

class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    in_play = models.BooleanField(default=False)
    turn = models.IntegerField(default=1)
    
    def player_cnt(self):
        return self.player_set.count()
    
    def set_in_play(self):
        self.in_play = True
        self.save()
    
    def update_turn(self):
        if self.turn < self.player_cnt():
            self.turn += 1
            self.save()
            print('plus 1', self.turn)
        else:
            self.turn = 1
            self.save()
            print('reset turn', self.turn)
            _round = Round.objects.get(game=self)
            _round.update_status()

class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bet = models.IntegerField(blank=True, null=True, default=None)
    wins = models.IntegerField(default=0)
    player_pos = models.IntegerField(blank=True, null=True, unique=True)
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}"
    
    def get_hand(self):
        return Card.objects.filter(player=self, status='h')
    
    def set_bet(self, bet:int):
        game = self.game
        game.update_turn()
        self.bet = bet
        self.save()
    
    def rotate_pos(self):
        self.player_pos += 1
        if self.player_pos > self.game.player_cnt():
            self.player_pos = 1
        
    def calc_rnd_pts(self):
        if self.bet == self.wins:
            self.points = 10 + self.bet
        

class Card(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True)
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
    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True)
    status = models.TextField(blank=True, choices=[('d', 'Deck'), ('h', 'Hand'),
                                                   ('p', 'Played'), ('t', 'Trump'),
                                                   ('i', 'In Play')],
                              default='d')

    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    @classmethod
    def create_deck(cls, game:Game=None):
        if game:
            cls.objects.filter(game=game).delete()
        
        deck = []
        for suit, _ in cls.SUIT_CHOICES:
            for rank, _ in cls.RANK_CHOICES:
                card = cls(suit=suit, rank=rank, game=game, status='d')
                deck.append(card)
        
        cls.objects.bulk_create(deck)
        return deck
    
    @classmethod
    def random_cards(cls, game:Game, num):
        deck = cls.objects.filter(game=game, status='d')
        cards = sample(list(deck), num)
        return cards
    
    @classmethod
    def deal(cls, game:Game, players:Player, num:int):
        _round = Round.objects.get_or_create(game=game)[0]
        _round = _round.update_status()
        for player in players:
            cards = cls.random_cards(game, num)
            for card in cards:
                card.player = player
                card.status = 'h'
            Card.objects.bulk_update(cards, ['player', 'status'])
        # set trump card
        trump = cls.random_cards(game, 1)[0]
        trump.status = 't'
        trump.save()
        return trump
    
    def play_card(self):
        # update with turn logic from game object
        game = self.game
        game.update_turn()
        self.status = 'i'
        self.save()
        
class Round(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    cur_round = models.IntegerField(default=7)
    trump = models.OneToOneField(Card, null=True, blank=True, on_delete=models.CASCADE)
    status = models.TextField(default='d',
                              choices=[('d', 'Deal'), 
                                       ('b', 'Bet'),
                                       ('p', 'Play'),])
    
    def cant_bet(self):
        players = self.game.player_set.all()
        bet_sum = players.aggregate(models.Sum('bet'))['bet__sum']
        if bet_sum and bet_sum < self.cur_round:
            return self.cur_round - bet_sum
    
    def next_round(self):
        # calculate round points and rotate player positions by 1
        for player in self.game.player_set.all():
            player.calc_rnd_pts()
            player.rotate_pos()
            player.bet = None
            player.save()
        self.cur_round -= 1
        if self.cur_round == 0:
            # calculate winner
            # end game
            pass
        # clear trump
        self.trump = None
        self.save()
        
    def update_status(self):
        if self.status == 'd':
            self.status = 'b'
        elif self.status == 'b':
            self.status = 'p'
        else:
            self.next_round()
            self.status = 'd'
        self.save()

