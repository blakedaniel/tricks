from django.test import TestCase
from django.contrib.auth.models import User
from ...models import Player, Round, Game, Card
from random import shuffle

# create test cases for player model
class PlayerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        deck = [Card.objects.create(suit=suit, rank=rank) for suit in ['s', 'c', 'd', 'h']
                for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']]
        shuffle(deck)
        
        users = [User.objects.create(username=f'user{idx}') for idx in range(1, 6)]
        players = [Player.objects.create(user=user) for user in users]
        for player in players:
            player.hand.add(*deck[:4])
            deck = deck[4:]
            player.save()
        
        game = Game.objects.create(num_of_rounds=7)
        game.players.add(*players)
        
        cur_round = Round.objects.create(id=1, game=game, num=3, dealer=players[0], cards_dealt=3, bet_sum=1)
        
        game.rounds.add(cur_round)
        game.save()

    def test_calc_score(self):
        player = Player.objects.get(id=1)
        
        player.bet = 0
        player.wins = 0
        player.calc_score()
        self.assertEqual(player.score, 10)
        
        player.bet = 3
        player.wins = 3
        player.calc_score()
        self.assertEqual(player.score, 23)
        
        player.bet = 3
        player.wins = 2
        player.calc_score()
        self.assertEqual(player.score, 23)

    def test_play_card(self):
        cur_round = Round.objects.get(id=1)
        card = cur_round.players.first().hand.first()
        player = cur_round.players.first()
        player.play_card(card, cur_round)
        self.assertTrue(card not in player.hand.all())
        self.assertTrue(card in cur_round.table.all())
        self.assertEqual(cur_round.trick, card)

        
    def test_bet_range(self):
        players = list(Player.objects.all())
        cur_round = Round.objects.get(id=1)
        self.assertEqual(players[0].bet_range(cur_round), [0, 1, 2, 3])
        self.assertEqual(players[1].bet_range(cur_round), [0, 1, 2, 3])
        self.assertEqual(players[2].bet_range(cur_round), [0, 1, 2, 3])
        self.assertEqual(players[3].bet_range(cur_round), [0, 1, 2, 3])
        self.assertEqual(players[4].bet_range(cur_round), [0, 1, 3])
    
    def test_set_bet(self):
        # get current game and current round
        game = Game.objects.get(id=1)
        cur_round = game.cur_round
        # get player1 and player2
        player1 = Player.objects.get(id=1)
        player2 = Player.objects.get(id=2)
        
        # Test set_bet function
        player1.set_bet(5, cur_round)
        self.assertEqual(player1.bet, 5)
        self.assertEqual(cur_round.bet_sum, 6)
        player2.set_bet(10, cur_round)
        self.assertEqual(player2.bet, 10)
        self.assertEqual(cur_round.bet_sum, 16)