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
from django_htmx.http import HttpResponseStopPolling, HttpResponseClientRefresh
# custom django imports
from .models import Card, Player, Round, Trick, Game

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
    return render(request, 'registration/register.html', {'form': form})


class CreateGame(View, LoginRequiredMixin):
    def get(self, request):
        # create new game
        game = Game.objects.filter(owner=request.user)
        if game.exists():
            game.delete()
            del request.session['game_details']
        game = Game.objects.get_or_create(owner=request.user)[0]
        cur_round = Round.objects.get_or_create(game=game)[0].cur_round
        player = Player.objects.get_or_create(game=game, user=request.user,
                                              player_pos=1)[0]
        cards_dealt = False
        request.session['game_details'] = {'cur_round': cur_round,
                                           'player_id': player.id,
                                           'game_id': game.id,
                                           'cards_dealt': cards_dealt,}
        return HttpResponseRedirect(reverse('game', args=(game.id,)))

class JoinGame(View):
    def post(self, request):
        # take game id from input field
        game_id = request.POST.get('game_id')
        game = Game.objects.get(id=game_id)
        
        cur_round = Round.objects.get_or_create(game=game)[0].cur_round
        player = Player.objects.get_or_create(game=game, user=request.user,)[0]
        if player.player_pos == None:
            player_pos = game.player_set.count() + 1
            player.player_pos = player_pos
            player.save()
        else:
            player_pos = player.player_pos
        cards_dealt = False
        # context.update({'game': game,
        #                 'cur_round': cur_round,
        #                 'players': Player.objects.filter(game=game),
        #                 'player': player,
        #                 'player_pos': player_pos,
        #                 'cards_dealt': cards_dealt,})
        request.session['game_details'] = ({'player_id': player.id,
                                            'cur_round': cur_round,
                                            'game_id': game_id,
                                            'player_pos': player_pos,
                                            'cards_dealt': cards_dealt,})
        return HttpResponseRedirect(reverse('game', args=(game.id,)))

class CurGame(View, LoginRequiredMixin):
    def get(self, request, game_id):
        context = request.session['game_details']
        game = Game.objects.get(id=game_id)
        deck = Card.objects.filter(game=game)
        players = Player.objects.filter(game=game)
        player = Player.objects.get(game=game, pk=context['player_id'])
        player_pos = player.player_pos
        player_hand = deck.filter(player=player)
        cards_dealt = len(player_hand) > 0
        cur_pile = deck.filter(status='i')
        trump = deck.filter(status='t')
        if trump.exists():
            trump = trump[0]
        else:
            trump = None
        # breakpoint()
        context.update({'game': game,
                        'players': players,
                        'player': player,
                        'player_pos': player_pos,
                        'deck': deck,
                        'player_hand': player_hand,
                        'cards_dealt': cards_dealt,
                        'trump': trump,
                        'cur_pile': cur_pile,})
        request.session['game_details'].update({'player_pos': player_pos,
                                                'cards_dealt': cards_dealt,})
        return render(request, 'game.html', context)
 

    
class Deal(View):
    def get(self, request, game_id):
        context = request.session['game_details']
        if request.user.is_authenticated:
            game = Game.objects.get(id=game_id)
        else:
            return HttpResponseRedirect(reverse('home'))
        
        if 'deal' in request.GET:
            game.in_play = True
            game.save()
            cur_round = context['cur_round']
            players = Player.objects.filter(game=game)
            Card.create_deck(game)
            trump = Card.deal(game, players, cur_round)
            request.session['game_details'].update({'trump_id': trump.id,})
            breakpoint()
            return HttpResponseRedirect(reverse('game', args=(game.id,)))

# class Bet(View):
#     context = {}

#     def set_bet(self, request, bet: int):
#         pass

#     def post(self, request, game_id):
#         pass

# def check_bets(request, game_id):
#     pass
