from django.test import TestCase
from django.contrib.auth.models import User
from ...models import Player, Round, Game
from collections import deque

# create test cases for player model
class GameTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        
        users = [User.objects.create(username=f'user{idx}') for idx in range(1, 4)]
        game = Game.objects.create(num_of_rounds=3)

    def test_start_new_round(self):
        game = Game.objects.get(id=1)
        users = list(User.objects.all())
        players = [Player.objects.create(user=cur_user, bet_pos=idx)
                   for idx, cur_user in enumerate(users)]
        game.players.add(*players)
        game.save()
        
        self.assertEqual(game.rounds.count(), 0)
        game.start_new_round()
        self.assertEqual(game.rounds.count(), 1)
        self.assertEqual(game.rounds.last().num, 3)
        self.assertEqual(game.rounds.last().dealer, Player.objects.get(user=users[0]))
        
        game.start_new_round()
        self.assertEqual(game.rounds.count(), 2)
        self.assertEqual(game.rounds.last().num, 2)
        self.assertEqual(game.rounds.last().dealer, Player.objects.get(user=users[1]))

    def test_round_complete(self):
        game = Game.objects.get(id=1)
        users = User.objects.all()
        players = [Player.objects.create(user=cur_user) for cur_user in users]
        cur_round = Round.objects.create(id=1, game=game, num=3, dealer=players[0], bet_sum=0)
        game.players.add(*players)
        game.rounds.add(cur_round)
        game.save()
        
        cur_round.deal_cards()
        self.assertFalse(game.check_round_complete())
        
        for player in cur_round.players.all():
            player.hand.clear()
            if player != cur_round.players.last():
                self.assertFalse(game.check_round_complete())
            else:
                self.assertTrue(game.check_round_complete())
        
    def test_add_player(self):
        game = Game.objects.get(id=1)
        self.assertEqual(game.players.count(), 0)
        
        player1 = Player.objects.create(user=User.objects.get(id=1))
        game.add_player(player1)
        self.assertEqual(game.players.count(), 1)
        self.assertEqual(player1.bet_pos, 0)
        self.assertEqual(player1.play_pos, 0)
        
        player2 = Player.objects.create(user=User.objects.get(id=2))
        game.add_player(player2)
        self.assertEqual(game.players.count(), 2)
        self.assertEqual(player2.bet_pos, 1)
        self.assertEqual(player2.play_pos, 1)
    
    def test_rotate_dealer(self):
        # create a game with 3 players
        game = Game.objects.get(id=1)
        users = User.objects.all()
        players = [Player.objects.create(user=cur_user) for cur_user in users]
        for player in players:
            game.add_player(player)
        self.assertEqual(game.players.count(), 3)

        # check the order of players
        self.assertEqual(players[0].bet_pos, 0)
        self.assertEqual(players[0].play_pos, 0)
        self.assertEqual(players[1].bet_pos, 1)
        self.assertEqual(players[1].play_pos, 1)
        self.assertEqual(players[2].bet_pos, 2)
        self.assertEqual(players[2].play_pos, 2)

        # rotate the dealer again
        players = game.rotate_dealer()

        # check the order of players
        self.assertEqual(players[1].bet_pos, 0)
        self.assertEqual(players[1].play_pos, 0)
        self.assertEqual(players[2].bet_pos, 1)
        self.assertEqual(players[2].play_pos, 1)
        self.assertEqual(players[0].bet_pos, 2)
        self.assertEqual(players[0].play_pos, 2)
        