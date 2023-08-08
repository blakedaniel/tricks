from collections import deque
from random import shuffle

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        
    def __str__(self):
        return f'{self.rank} of {self.suit}'
    
    def __repr__(self):
        return f'{self.rank} of {self.suit}'
    
    def compare_rank(self, winning_card, trump_suit):
        if self.suit == winning_card.suit:
            return self.rank > winning_card.rank
        elif self.suit == trump_suit:
            return True
        else:
            return False

class Player:
    def __init__(self, user):
        self.user = user
        self.hand = None
        self.bet = None
        self.wins = 0
        self.score = 0

    def __str__(self):
        return f'{self.user}'
    
    def __repr__(self):
        return f'{self.user}'
    
    def invalid_card(self, hand, card_idx, round):
        if card_idx < 0 or card_idx >= len(hand):
            return True
        
        card = hand[card_idx]
        playable_cards = [card for card in self.hand if card.suit == round.trick_suit]
        
        if len(playable_cards) == 0:
            playable_cards = self.hand
        else:
            playable_cards += [card for card in self.hand
                               if card.suit == round.trump_suit]
        if card in playable_cards:
            return False
        return True
        
    def play_card(self, round):
        for op_num, card in zip(range(len(self.hand)), self.hand):
            print(f'{op_num}: {card}')
        card_idx = int(input(f'{self.user}, which card will you play? '))
        while self.invalid_card(self.hand, card_idx, round):
            print('Invalid card. Try again.')
            card_idx = int(input(f'{self.user}, which card will you play? '))
        card = self.hand.pop(card_idx)
        return card
    
    def calc_score(self):
        if self.bet == self.wins:
            self.score += 10 + self.bet

class Round:
    def __init__(self, round_num:int, players:deque):
        self.num = round_num
        self.players = players.copy()
        self.dealer = self.players[0]
        self.trump_suit = None
        self.trick_suit = None
        self.cards_dealt = self.num
        self.bet_sum = 0
    
    def deal_cards(self):
        self.deck = [Card(suit, rank)
                     for suit in ['Spades', 'Hearts', 'Clubs', 'Diamonds']
                     for rank in range(2, 15)]
        shuffle(self.deck)
        
        players = self.players
        for player in players:
            player.hand = [self.deck.pop() for _ in range(self.num)]
        self.trump_suit = self.deck.pop().suit
        
    def rotate_players(self, players:deque[Player], starting_player:Player):
        start_idx = players.index(starting_player)
        players.rotate(-start_idx)
        
    def invalid_bet(self, player, bet):
        if bet == None:
            return True
        if player == self.players[-1] and bet == (self.cards_dealt - self.bet_sum):
            return True
        return False
        
    def take_bets(self):
        players = self.players
        players.rotate(-1)
        for player in players:
            while self.invalid_bet(player, player.bet):
                print(f'''{player.user}, you have {player.hand} in your hand
                      and the trump suit is {self.trump_suit}.''')
                bet = int(input(f'{player.user}, how many tricks will you win? '))
                if self.invalid_bet(player, bet):
                    print('Invalid bet. Try again.')
                else:
                    player.bet = bet
                    self.bet_sum += player.bet
            
    def play_trick(self, players:deque[Player]):
        winner = None # (player, card)
        print('play order:', players)
        for player in players:
            card = player.play_card(self)
            if not winner:
                winner = (player, card)
                self.trick_suit = card.suit
            elif card.compare_rank(winner[1], self.trump_suit):
                winner = (player, card)
        winning_player = winner[0]
        winning_player.wins += 1
        print(winning_player, 'wins the trick!')
        self.rotate_players(players, winning_player)
        
    def play_tricks(self):
        players = self.players
        for _ in range(self.num):
            self.play_trick(players)
        
    def calc_scores(self):
        players = self.players
        for player in players:
            player.calc_score()

    def __str__(self):
        return f'Round {self.num}'

class Game:
    def __init__(self, users, num_of_rounds=7):
        self.players = deque([Player(user) for user in users])
        self.num_of_rounds = num_of_rounds
        self.rounds = []

    def __str__(self):
        return f'Game {self.id}'

    @property
    def cur_round(self):
        if len(self.rounds) > 0:
            return self.rounds[-1]

    def rotate_dealer(self):
        self.players.rotate(-1)
        
    def clear_bets(self):
        for player in self.players:
            player.bet = None

    def start_game(self):
        for rnd_num in range(self.num_of_rounds, 0, -1):
            print(f'Starting round {rnd_num}...')
            rnd_obj = Round(rnd_num, self.players)
            # deal cards
            rnd_obj.deal_cards()
            # take bets
            rnd_obj.take_bets()
            # play tricks
            rnd_obj.play_tricks()
            # calc scores
            rnd_obj.calc_scores()
            # track prev round
            self.rounds.append(rnd_obj)
            # clear bets
            self.clear_bets()
            # rotate dealer
            self.rotate_dealer()
            
    def end_game(self):
        winners = []
        players = self.players
        for player in players:
            if not winners:
                winners.append(player)
            elif player.score == winners[0].score:
                winners.append(player)
            elif player.score > winners[0].score:
                winners = [player,]
        for winner in winners:
            print(f'{winner} wins!')

if __name__ == "__main__":
    # Create the game with player names
    player_names = ["Player1", "Player2", "Player3"]
    game = Game(player_names, 2)

    # Start the game
    game.start_game()

    # End the game and determine the winner
    game.end_game()