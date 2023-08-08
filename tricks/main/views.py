# standard django libraries
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
# from django_htmx libraries
from django_htmx.http import HttpResponseStopPolling, HttpResponseClientRefresh
# custom django imports
from .models import Card, Player, Round, Game
# python libraries
from collections import deque

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
        player = Player.objects.create(user=request.user)
        game = Game.objects.create(players=[player,], num_of_rounds=7)
        request.session['game_details'] = {'player_id': player.id,
                                           'game_id': game.id,}
        return HttpResponseRedirect(reverse('game', args=(game.id,)))

class JoinGame(View):
    def post(self, request):
        # take game id from input field
        game_id = request.POST.get('game_id')
        game = Game.objects.get(id=game_id)
        if game.in_play:
            HttpResponse('Game in progress. Try another game.')
        player = Player.objects.create(user=request.user,)
        game.players.add(player)
        request.session['game_details'] = ({'player_id': player.id,
                                            'game_id': game_id,})
        return HttpResponseRedirect(reverse('game', args=(game.id,)))

class CurGame(View, LoginRequiredMixin):
    def get(self, request, game_id):
        context = request.session['game_details'].copy()
        if request.user.is_authenticated:
            game = Game.objects.get(id=game_id)
        else:
            return HttpResponseRedirect(reverse('home'))
        cur_round = game.cur_round
        player = Player.objects.get(id=context['player_id'])
        players = game.players.all()
        bet_order = deque(players.all())
        bet_idx = game.bet_turn
        play_order = deque(cur_round.players.all())
        play_idx = len(cur_round.table.all())
        context.update({'game': game,
                        'cur_round': cur_round,
                        'bet_order': bet_order,
                        'play_order': play_order,
                        'betting_player': bet_order[bet_idx],
                        'playing_player': play_order[play_idx],
                        'bet_range': player.bet_range(cur_round),
                        'dealer': cur_round.dealer,
                        'trump': cur_round.trump,
                        'trick': cur_round.trick,
                        'player': player,
                        'table': cur_round.table.all(),
                        'bet': player.bet,
                        'wins': player.wins,
                        'score': player.score,})
        return render(request, 'game.html', context)
 

    
class StartGame(View):
    def get(self, request, game_id):
        if request.user.is_authenticated:
            game = Game.objects.get(id=game_id)
        else:
            return HttpResponseRedirect(reverse('home'))
        
        if 'start_game' in request.GET:
            round_nums = [num for num in range(game.num_of_rounds, 0, -1)]
            cur_round = Round.objects.create(num=round_nums[len(game.rounds.all())],
                                             players=game.players.all(),
                                             dealer=game.players.first(),)
            game.rounds.add(cur_round)
            cur_round.deal_cards()
            request.session['game_details']['round_id'] = cur_round.id
            request.session.save()
            return HttpResponseRedirect(reverse('game', args=(game.id,)))

class Bet(View):
    def post(self, request, game_id):
        context = request.session['game_details']
        
        if 'bet' in request.POST:
            game = Game.objects.get(id=game_id)
            player = Player.objects.get(id=context['player_id'])
            bet = int(request.POST.get('bet'))
            player.set_bet(bet)
            game.bet_turn += 1
            game.save()
            return HttpResponseRedirect(reverse('game', args=(game.id,)))


class PlayCard(View):
    def post(self, request, game_id):
        if 'play_card' in request.POST:
            context = request.session['game_details']
            player = Player.objects.get(id=context['player_id'])
            game = Game.objects.get(id=game_id)
            cur_round = game.cur_round
            card_id = request.POST.get('play_card')
            card = Card.objects.get(id=card_id)
            player.play_card(card, cur_round)
            if cur_round.check_trick_complete():
                if cur_round.num != 1 and game.check_round_complete():
                    game.start_new_round()
                elif cur_round.num == 1 and game.check_round_complete():
                    winners = game.end_game()
                    return render(request, 'end_game.html',
                                  {'winners': winners,
                                   'players': game.players.all(),})
            return HttpResponseRedirect(reverse('game', args=(game.id,)))