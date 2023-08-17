# standard django libraries
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
# from django_htmx libraries
from django_htmx.http import HttpResponseClientRedirect, HttpResponseStopPolling 
# custom django imports
from .models import Card, Player, Game
# python libraries
import time

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
        player = Player.objects.create(user=request.user)
        game = Game.objects.create(num_of_rounds=7)
        game.players.add(player)
        request.session['game_details'] = {'player_id': player.id,
                                           'game_id': game.id,}
        return HttpResponseRedirect(reverse('game', args=(game.id,)))

class JoinGame(View, LoginRequiredMixin):
    def post(self, request):
        # take game id from input field
        game_id = request.POST.get('game_id')
        game = Game.objects.get(id=game_id)
        if game.in_play:
            HttpResponse('Game in progress. Try another game.')
        players = game.players.all()
        player_not_in_game =  players.filter(user=request.user).count() == 0
        if player_not_in_game:
            player = Player.objects.create(user=request.user,)
            game.add_player(player)
        else:
            player = players.get(user=request.user)
        request.session['game_details'] = ({'player_id': player.id,
                                            'game_id': game_id,})
        return HttpResponseRedirect(reverse('game', args=(game.id,)))

class CurGame(View, LoginRequiredMixin):
    def update_cur_round_data(self, game, context, cur_round, players, player):
            play_order = game.players.order_by('play_pos')
            remaining_plaing_players = game.players.filter(cur_card__isnull=True).order_by('play_pos')
            playing_player = remaining_plaing_players.first()
            bet_range = player.bet_range(cur_round)
            card_play_ready = cur_round.players.filter(bet__isnull=True).count() == 0
            playable_cards = player.playable_cards(cur_round)
            context.update({
                'cur_round': cur_round,
                'playing_order': play_order,
                'playing_player': playing_player,
                'bet_range': bet_range,
                'dealer': cur_round.dealer,
                'trump': cur_round.trump,
                'trick': cur_round.trick,
                'table': cur_round.table.all(),
                'card_play_ready': card_play_ready,
                'playable_cards': playable_cards,
                })
            
    def update_game_play_data(self, game, context, players, player):
        bet_order = game.players.order_by('bet_pos')
        remaining_betting_players = game.players.filter(bet__isnull=True).order_by('bet_pos')
        betting_player = remaining_betting_players.first()
        hand = player.hand.all().order_by('suit', 'rank')
        context.update({'game': game,
                        'players': players,
                        'player': player,
                        'betting_order': bet_order,
                        'betting_player': betting_player,
                        'hand': hand,
                        'bet': player.bet,
                        'wins': player.wins,
                        'score': player.score,})
        
    def update_last_round_data(self, game, context, player):
            other_players = game.players.exclude(id=player.id)
            others_cards = [player.hand.first() for player in other_players]
            last_card = player.hand.last()
            context.update({'others_cards': others_cards,
                            'last_card': last_card,})
    
    def get(self, request, game_id):
        context = request.session['game_details'].copy()
        if request.user.is_authenticated:
            game = Game.objects.get(id=game_id)
        else:
            return HttpResponseRedirect(reverse('home'))
        player = Player.objects.get(id=context['player_id'])
        players = game.players.all().order_by('score')
        cur_round = game.cur_round
        if cur_round:
            self.update_cur_round_data(game, context, cur_round, players, player)
        
        self.update_game_play_data(game, context, players, player)
        
        last_round = cur_round and cur_round.num == 1
        if last_round:
            self.update_last_round_data(game, context, player)

        return render(request, 'game.html', context)
    
class StartGame(View):
    def get(self, request, game_id):
        if request.user.is_authenticated:
            game = Game.objects.get(id=game_id)
        else:
            return HttpResponseRedirect(reverse('home'))
        
        if 'start_game' in request.GET:
            cur_round = game.start_new_round()
            request.session['game_details']['round_id'] = cur_round.id
            request.session.save()
            return HttpResponseRedirect(reverse('game', args=(game.id,)))

class Bet(View):
    def post(self, request, game_id):
        context = request.session['game_details']
        
        if 'bet' in request.POST:
            game = Game.objects.get(id=game_id)
            cur_round = game.cur_round
            player = Player.objects.get(id=context['player_id'])
            bet = int(request.POST.get('bet'))
            player.set_bet(bet, cur_round)
            game.bet_turn += 1
            game.bet_turn %= len(game.players.all())
            game.save()
            return HttpResponseRedirect(reverse('game', args=(game.id,)))


class PlayCard(View):
    def post(self, request, game_id):
        game = Game.objects.get(id=game_id)
        cur_round = game.cur_round
        context = request.session['game_details']
        player = Player.objects.get(id=context['player_id'])
        
        if 'play_card' in request.POST:
            card_id = request.POST.get('play_card')
            card = Card.objects.get(id=card_id)
            player.play_card(card, cur_round)
            if cur_round.check_trick_complete():
                cur_round.end_trick()
                time.sleep(3)
                cur_round.start_new_trick()
                if cur_round.num != 1 and game.check_round_complete():
                    game.end_round()
                    game.start_new_round()
            return HttpResponseRedirect(reverse('game', args=(game.id,)))
        if 'play_last_card' in request.POST:
            card_id = request.POST.get('play_last_card')
            card = Card.objects.get(id=card_id)
            player.play_card(card, cur_round)
            return HttpResponseRedirect(reverse('game', args=(game.id,)))
    
class SidebarUpdate(CurGame):
    def get(self, request, game_id):
        game = Game.objects.get(id=game_id)
        context = request.session['game_details'].copy()
        if request.htmx:
            status = 200
            player = Player.objects.get(id=context['player_id'])
            players = game.players.all().order_by('score')
            cur_round = game.cur_round
            if cur_round:
                self.update_cur_round_data(game, context, cur_round, players, player)
            
            self.update_game_play_data(game, context, players, player)
            
            if 'last_round' in context and context['last_round']:
                self.update_last_round_data(game, context, player)
                if game.finished:
                    status = 286
            return render(request, 'blocks/sidebar.html', context, status=status)

class GamePlayUpdate(CurGame):
    def end_game(self, game, context):
        cur_round = game.cur_round
        if not game.finished:
            cur_round.end_trick()
            time.sleep(3)
            game.end_round()
            game.end_game()
        winners = game.get_winners()
        players = game.players.all().order_by('score')
        context.update({'players': players,
                        'winners': winners,})
    
    def get(self, request, game_id):
        game = Game.objects.get(id=game_id)
        context = request.session['game_details'].copy()
        if request.htmx:
            player = Player.objects.get(id=context['player_id'])
            players = game.players.all().order_by('score')
            cur_round = game.cur_round
            if cur_round:
                self.update_cur_round_data(game, context, cur_round, players, player)
                
            self.update_game_play_data(game, context, players, player)
            
            if cur_round and cur_round.num == 1:
                self.update_last_round_data(game, context, player)
                if cur_round.check_trick_complete():
                    self.end_game(game, context)
                    return render(request, 'blocks/table_game_finished.html',
                                  context, status=286)
            return render(request, 'blocks/table.html', context)