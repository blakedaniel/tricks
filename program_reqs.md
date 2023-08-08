# Game:
Represents the overall card game, managing the rounds, players, and scoring.
## Attributes:
- players: List of Player objects representing the players in the game.
- rounds: List of Round objects representing the rounds in the game.
- current_round: Integer indicating the current round being played.
## Methods:
- start_game(): Initializes the game, creates players, and starts the first round.
- play_round(): Manages the flow of a round, dealing cards, taking bets, playing tricks, and updating scores.
- end_game(): Determines the winner based on the players' scores and ends the game.

# Round:
Represents each round of the card game, including the dealer, trump suit, and number of tricks to be won.
## Attributes:
- round_number: Integer representing the round number (7 to 1).
- dealer: Player object representing the dealer for the round.
- trump_suit: String representing the trump suit for the round.
- tricks_to_win: Integer indicating the number of tricks to be won in the round.
- cards_dealt: Integer representing the number of cards initially dealt to each player in the round.
- play_order: List of Player objects representing the order of play for the round.
- bet_order: List of Player objects representing the order of bets for the round.
## Methods:
- deal_cards(): Deals the appropriate number of cards to each player for the round. 
- set_trump_suit(card): Sets the trump suit based on the last card flipped over by the dealer.
- take_bets(): Takes bets from each player for the current round.
- play_trick(starting_player): Manages the flow of a trick, including card plays and determining the winner.

# Player:
Represents a player in the game, keeping track of their hand, bet, and score.
## Attributes:
- name: String representing the name or identifier of the player.
- hand: List of Card objects representing the cards in the player's hand for the current round.
- bet: Integer representing the number of tricks the player bets to win in the current round.
- score: Integer representing the player's total score.
## Methods:
- play_card(trick_suit, trick_number): Chooses and plays a card from their hand for a given trick.
- calculate_score(round_result): Updates the player's score based on the result of the round.

# Card:
Represents a playing card, including its suit and value.
## Attributes:
- suit: String representing the suit of the card (e.g., "Hearts," "Diamonds," "Clubs," "Spades").
- value: String or Integer representing the value or rank of the card.
## Methods:
- compare_value(other_card, trump_suit): Compares the value of the current card with another card to determine the winner of a trick based on the trick suit and trump suit.