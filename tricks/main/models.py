from django.db import models
from django.contrib.auth.models import User
from random import sample

class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bet = models.IntegerField(blank=True, null=True, default=None)
    player_pos = models.IntegerField(blank=True, unique=True)
    points = models.IntegerField(default=0)

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
        
class Round(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    cur_round = models.IntegerField(default=7)
    trump = models.OneToOneField(Card, null=True, blank=True, on_delete=models.CASCADE)

class Trick(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    trick_rnd = models.PositiveSmallIntegerField(default=1)
    cards_played = models.ManyToManyField(Card, blank=True)
    winner = models.OneToOneField(Player, blank=True, on_delete=models.CASCADE, related_name='winner')

