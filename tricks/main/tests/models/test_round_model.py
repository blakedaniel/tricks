from django.test import TestCase
from django.contrib.auth.models import User
from ...models import Player, Round, Game, Card

# create test cases for player model
class RoundTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        
        users = [User.objects.create(username=f'user{idx}') for idx in range(1, 4)]
        players = [Player.objects.create(user=user, bet_pos=idx, play_pos=idx)
                   for idx, user in enumerate(users)]
        
        game = Game.objects.create(num_of_rounds=3)
        game.players.add(*players)
        
        cur_round = Round.objects.create(id=1, game=game, num=3, dealer=players[0],
                                         bet_sum=0)
        game.rounds.add(cur_round)
        game.save()

    def test_trick_winner(self):
        game = Game.objects.get(id=1)
        cur_round = game.cur_round
        cur_round.trump = Card.objects.create(rank=3, suit='s')
        cur_round.trick = Card.objects.create(rank=10,suit='c')
        game.save()
        
        player1 = game.players.get(play_pos=0)
        player1.cur_card = Card.objects.create(rank=10, suit='c')
        player1.save()
        
        player2 = game.players.get(play_pos=1)
        player2.cur_card = Card.objects.create(rank=8, suit='c')
        player2.save()
        
        player3 = game.players.get(play_pos=2)
        player3.cur_card = Card.objects.create(rank=8, suit='h')
        player3.save()
        game.players.set([player1, player2, player3], clear=True)
        
        # first player wins
        winner = cur_round.get_trick_winner()
        self.assertEqual(winner.user.username, 'user1')
        
        # second player wins (trick suit)
        player1.cur_card = Card.objects.create(rank=10, suit='c')
        player1.save()
        player2.cur_card = Card.objects.create(rank=12, suit='c')
        player2.save()
        player3.cur_card = Card.objects.create(rank=8, suit='h')
        player3.save()
        
        game.players.set([player1, player2, player3], clear=True)
        winner = cur_round.get_trick_winner()
        self.assertEqual(winner.user.username, 'user2')
        
        # third player wins (trump suit)
        player1.cur_card = Card.objects.create(rank=10, suit='c')
        player1.save()
        player2.cur_card = Card.objects.create(rank=12, suit='c')
        player2.save()
        player3.cur_card = Card.objects.create(rank=2, suit='s')
        player3.save()
        
        game.players.set([player1, player2, player3], clear=True)
        winner = cur_round.get_trick_winner()
        self.assertEqual(winner.user.username, 'user3')
        
    def test_update_play_order_rotate_1(self):
        game = Game.objects.get(id=1)
        cur_round = game.cur_round
        # player_objs: <QuerySet [user1, user2, user3]
        players = list(cur_round.players.all().order_by('play_pos'))
        for idx, player in enumerate(players):
            print(player, player.play_pos)
            self.assertEqual(players[idx].user.username, f'user{idx+1}')

        starting_player = players[1]
        cur_round.update_play_order(starting_player)
        updated_players = list(cur_round.players.all().order_by('play_pos'))
        self.assertEqual(players[1].user.username, updated_players[0].user.username)
        self.assertEqual(players[2].user.username, updated_players[1].user.username)
        self.assertEqual(players[0].user.username, updated_players[2].user.username)
        
    def test_update_play_order_rotate_2(self):
        game = Game.objects.get(id=1)
        cur_round = game.cur_round
        # player_objs: <QuerySet [user1, user2, user3]
        players = list(cur_round.players.all().order_by('play_pos'))
        for idx, player in enumerate(players):
            print(player, player.play_pos)
            self.assertEqual(players[idx].user.username, f'user{idx+1}')
        
        starting_player = players[2]
        cur_round.update_play_order(starting_player)
        updated_players = list(cur_round.players.all().order_by('play_pos'))
        self.assertEqual(players[2].user.username, updated_players[0].user.username)
        self.assertEqual(players[0].user.username, updated_players[1].user.username)
        self.assertEqual(players[1].user.username, updated_players[2].user.username)
    
    def test_update_play_order_rotate_0(self):
        game = Game.objects.get(id=1)
        cur_round = game.cur_round
        # player_objs: <QuerySet [user1, user2, user3]
        players = list(cur_round.players.all().order_by('play_pos'))
        for idx, player in enumerate(players):
            print(player, player.play_pos)
            self.assertEqual(players[idx].user.username, f'user{idx+1}')
        
        starting_player = players[0]
        cur_round.update_play_order(starting_player)
        updated_players = list(cur_round.players.all().order_by('play_pos'))
        self.assertEqual(players[0].user.username, updated_players[0].user.username)
        self.assertEqual(players[1].user.username, updated_players[1].user.username)
        self.assertEqual(players[2].user.username, updated_players[2].user.username)

    # def test_check_trick_complete(self):
    #     cur_round = Round.objects.get(id=1)
    #     player_objs = cur_round.players.all()
    #     players = list(player_objs)
    #     cur_round.deal_cards()
        
    #     # check that trick is not complete
    #     ## check that table is empty
    #     self.assertFalse(cur_round.check_trick_complete())
        
    #     ## check that table has fewer cards than players
    #     for player_idx in range(len(players) - 1):
    #         player = players[player_idx]
    #         print(player.hand)
    #         card = player.hand.first()
    #         player.play_card(card, cur_round)
    #     self.assertFalse(cur_round.check_trick_complete())
        
    #     # check that trick is complete
    #     player = player_objs.last()
    #     card = player.hand.first()
    #     player.play_card(card, cur_round)
    #     cur_round.check_trick_complete()
       
    #     ## check that table has as many cards as players
    #     self.assertEqual(cur_round.table.count(), len(players))
        
    #     ## check that sum of player.wins is 1
    #     players = list(cur_round.players.all())
    #     self.assertEqual(sum([player.wins for player in players]), 1)
       
    #     ## check that player.cur_card is None
    #     players_cur_cards = [player.cur_card for player in players]
    #     self.assertEqual(players_cur_cards, [None for _ in range(len(players))])
    
    # def test_deal_cards(self):
    #     cur_round = Round.objects.get(id=1)
    #     self.assertEqual(cur_round.deck.count(), 0)
    #     self.assertEqual(cur_round.players.count(), 5)
    #     self.assertEqual(cur_round.trump, None)
    #     self.assertEqual(cur_round.cards_dealt, 0)
        
    #     cur_round.deal_cards()
        
    #     self.assertEqual(cur_round.deck.count(), 51 - (cur_round.players.count() * cur_round.cards_dealt))
    #     self.assertEqual(cur_round.players.count(), 5)
    #     self.assertNotEqual(cur_round.trump, None)
    #     self.assertEqual(cur_round.cards_dealt, 3)