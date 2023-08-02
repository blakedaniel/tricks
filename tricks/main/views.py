# standard django libraries
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
# from django_htmx libraries
from django_htmx.http import HttpResponseStopPolling
# custom django imports
from .models import Card, Player, Round, Trick, Game
# python libraries
from random import sample

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


class CreateGame(View, LoginRequiredMixin):
    template_name = 'game.html'
        
    def get(self, request):
        context = {}
        # create new game
        game = Game.objects.get_or_create(owner=request.user)[0]
        cur_round = Round.objects.get_or_create(game=game)[0].cur_round
        player = Player.objects.get_or_create(game=game, user=request.user)[0]
        players = Player.objects.filter(game=game)
        context.update({'game': game,
                        'cur_round': cur_round,
                        'player': player,
                        'players': players,})
        request.session['game_details'] = {'cur_round': cur_round,
                                           'player_id': player.id,
                                           'game_id': game.id,}
        return HttpResponseRedirect(reverse('game', args=(game.id,)), context)

class CurGame(View, LoginRequiredMixin):
    def get(self, request, game_id):
        context = request.session['game_details']
        game = Game.objects.get(id=game_id)
        deck = Card.objects.filter(game=game)
        players = Player.objects.filter(game=game)
        player = Player.objects.get(game=game, pk=context['player_id'])
        player_pos = player.player_pos
        player_hand = deck.filter(player=player)
        cur_pile = deck.filter(status='i')
        context.update({'game': game,
                        'players': players,
                        'player': player,
                        'player_pos': player_pos,
                        'deck': deck,
                        'player_hand': player_hand,
                        'cur_pile': cur_pile,})
        request.session['game_details'].update({'player_pos': player_pos,})
        return render(request, 'game.html', context)
 
class JoinGame(View):
    template_name = 'game.html'
    
    def post(self, request):
        # take game id from input field
        context = {}
        game_id = request.POST.get('game_id')
        game = Game.objects.get(id=game_id)
        cur_round = Round.objects.get_or_create(game=game)[0].cur_round
        player_pos = game.player_set.count() + 1
        player = Player.objects.create(game=game, user=request.user,
                                       player_pos=player_pos)[0]
        context.update({'game': game,
                        'cur_round': cur_round,
                        'players': Player.objects.filter(game=game),
                        'player': player,
                        'player_pos': player_pos,})
        request.session['game_details'].update({'player_id': player.id,
                                                'cur_round': cur_round,
                                                'game_id': game_id,
                                                'player_pos': player_pos,})
        return HttpResponseRedirect(reverse('game', args=(game.id,)), context)
    

class Deal(View):
    template_name = 'game.html'

    def get(self, request, game_id):
        context = request.session['game_details']
        if request.user.is_authenticated:
            game = Game.objects.get(id=game_id)
        else:
            return HttpResponseRedirect(reverse('home'))
        
        if 'deal' in request.GET:
            cur_round = context['cur_round']
            player = Player.objects.get(game=game, pk=context['player_id'])
            players = Player.objects.filter(game=game)
            Card.create_deck(game)
            trump = Card.deal(game, players, cur_round)
            player_hand = Card.objects.filter(game=game, player=player)
            context.update({'game': game,
                            'deck': Card.objects.filter(game=game),
                            'trump': trump,
                            'players': players,
                            'player': player,
                            'player_hand': player_hand,})
            request.session['game_details'].update({'trump_id': trump.id,})
            if request.htmx.target == 'updated_sidebar':
                breakpoint()
                # return HttpResponse('<p>THIS IS A TEST</p>', content_type='text/html')
                return render(request, 'blocks/sidebar_after_deal.html', context)
            else:
                return render(request, 'game.html', context)

# class Bet(View):
#     context = {}

#     def set_bet(self, request, bet: int):
#         pass

#     def post(self, request, game_id):
#         pass

# def check_bets(request, game_id):
#     pass
