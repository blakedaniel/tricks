from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth import authenticate
from ..models import Game, Player
from ..views import CreateGame

class CreateGameTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_game(self):
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('create_game'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/game/1/')
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Player.objects.count(), 1)
        self.assertEqual(Game.objects.get().num_of_rounds, 7)
        self.assertEqual(Game.objects.get().players.get().user.username, 'test')