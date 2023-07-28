# standard django libraries
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
# custom django imports
from .models import Card, Player, Round, Trick, Game
# python libraries
from random import sample

# TODO: fix htmx issue with showing form for current betting_player
## steps taken so far:
## ensured that all url patterns are unique
## ensured that players are coming through context
## ensured that betting_player is coming through context
## ensured that betting_player == current user
## next steps: read about Django Channels and see if that will help
## https://channels.readthedocs.io/en/latest/introduction.html
## https://channels.readthedocs.io/en/latest/

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def deal(request, )

class CreateGame(View):
    template_name = 'main_temp.html'
    
    def create_deck(self, game:Game):
        suits = ['h', 'd', 'c', 's']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'j', 'q', 'k', 'a']
        deck = [(suit, value) for suit in suits for value in values]
        if Card.objects.filter(game=game).exists():
            Card.objects.bulk_update(Card.objects.filter(game=game), ['player_id'])
        else:
            Card.objects.bulk_create([Card(suit=suit, rank=rank, game=game)
                                      for suit, rank in deck])
        
    def get(self, request):
        # create new game
        game = Game.objects.get_or_create(owner=request.user)
        game = game[0]
        # create deck
        self.create_deck(game)
        Player.objects.get_or_create(game=game, user=request.user, player_pos=1)
        return HttpResponseRedirect(reverse('game', args=(game.id,)))
    
class JoinGame(View):
    template_name = 'main_temp.html'
    
    def post(self, request):
        game_id = request.POST.get('game_id')
        game = Game.objects.get(id=game_id)
        player_pos = game.player_set.count() + 1
        Player.objects.create(game=game, user=request.user, player_pos=player_pos)
        return HttpResponseRedirect(reverse('game', args=(game_id,)))

class MainGame(View):
    template_name = 'game.html'
    context = {}
    
    def random_cards(self, game:Game, num:int):
        avail_deck = Card.objects.filter(player=None, game=game)
        card_ids = list(avail_deck.values_list('id', flat=True))
        card_ids = sample(card_ids, num)
        cards = avail_deck.filter(player=None, id__in=card_ids)
        return cards
    
    def deal(self, game:Game, game_round:Round):
        # breakpoint()
        # reset player bets to None
        Player.objects.filter(game=game).update(bet=None)
        # set player_id of game cards to None
        avail_deck = Card.objects.filter(game=game)
        for card in avail_deck:
            card.player = None
        Card.objects.bulk_update(avail_deck, ['player_id'])
        # deal cards to players
        players = Player.objects.filter(game=game)
        for player in players:
            player_cards = self.random_cards(game, game_round.cur_round)
            for card in player_cards:
                card.player = player
                card.status = 'h'
            Card.objects.bulk_update(player_cards, ['player_id', 'status'])
        # set trump suite
        game_round.trump = self.random_cards(game, 1).first()
        game_round.trump.status = 't'
        game_round.trump.save()
        return players
    
    def get(self, request, game_id):
        # breakpoint()
        context = self.context
        if request.user.is_authenticated:
            game= Game.objects.get(id=game_id)
        else:
            return HttpResponseRedirect(reverse('home'))
        
        game_round = Round.objects.get_or_create(game=game)[0]
        if 'deal' in request.GET:
            # deal cards to players and set trump
            players = self.deal(game, game_round)
            players = players.order_by('player_pos')
            betting_player = players.first()
            context.update({'game_id': game.id,
                   'trump_card': game_round.trump,
                   'betting_player': betting_player,
                   'cur_round': game_round.cur_round,})
            # breakpoint()
            if request.htmx.target == 'updated_sidebar':
                # breakpoint()
                return render(request, 'blocks/sidebar_after_deal.html', context)
            else:
                return render(request, self.template_name, context)
        elif request.htmx.target == 'bet_form' and 'betting_player' in context:
            cur_round = int(context['cur_round'])
            betting_player = context['betting_player']
            cant_bet = context.get('cant_bet', None)
            bets  = [i for i in range(0, cur_round +1)]
            if cant_bet in bets:
                bets = bets.remove(cant_bet)
            context.update({'bets': bets,})
            if request.htmx and request.user == betting_player.user:
                return render(request, 'blocks/game_bet_form.html', context)
        else:
            players = Player.objects.filter(game=game)
            players = players.order_by('player_pos')
            context.update({'game_id': game.id,
                   'cur_round': game_round.cur_round,
                   'players': players,
                   'player_cnt': len(players),})
            return render(request, self.template_name, context)
        
    def set_bet(self, game:Game, player:Player, bet:int):
        player.bet = bet
        player.save()
        return player.player_pos + 1
    
    def post(self, request, game_id):
        # breakpoint()
        context = self.context
        players = context['players']
        print(request.POST)
        if 'bet' in request.htmx.POST:
            player = Player.objects.get(user=request.user)
            game = Game.objects.get(id=game_id)
            bet = int(request.POST.get('bet'))
            bet_turn = self.set_bet(game, player, bet)
            betting_player = Player.objects.get(game=game, player_pos=bet_turn)
            cant_bet = Player.objects.aggregate(cant_bet=Round.objects
                                                .get(game=game).cur_round - Sum('bet'))['cant_bet']
            # breakpoint()
            context.update({'betting_player': betting_player,
                            'cant_bet': cant_bet,
                            'players': players,})
            return HttpResponseRedirect(reverse('game', args=(game_id,)))