# Tricks

Tricks is a trick-based card game where players try to bet on the number of 'tricks' they will win in a round. A trick is a 'sub-round' of play where each player plays a card. The player who plays the highest card wins the trick. The game is played over a series of rounds, with the first round consists of 7 cards, and every subsequent round the cards dealt decreases by one. The final round is played with one card, and players see other players cards, but not their own make bets based off of this information. Players get points if the bet they set at the start of each round equals the number of tricks they won in that round. The player with the most points at the end of the game wins.

## See Demo
Check out the demo [here](https://tricks.fly.dev).

## run locally
### Requirements
- python 3.9+
- django 4.0.1+
- docker 20.10.8+

### Steps
1. Clone the repo
2. Run `pip install -r requirements.txt`
3. Run `docker-compose up` from `tricks/tricks`
4. Run `python manage.py makemigrations` from `tricks/tricks`
5. Run `python manage.py migrate` from `tricks/tricks`
6. Run `python manage.py createsuperuser` from `tricks/tricks`
7. Run `python manage.py collectstatic` from `tricks/tricks`
8. Run `python manage.py runserver` from `tricks/tricks`
9. Navigate to `localhost:8000` in your browser

## cardMaker.py
This script is used to generate the card images used in the game. It uses the [Pillow](https://pillow.readthedocs.io/en/stable/) library to generate the images. The script takes in a single image of 52 cards, and crops each card out of the image and saves it as a separate image.