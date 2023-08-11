from django.test import TestCase
from ...models import Card

class CardTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        card1 = Card.objects.create(suit='s', rank='2')
        card2 = Card.objects.create(suit='s', rank='3')
        card3 = Card.objects.create(suit='c', rank='2')
        card4 = Card.objects.create(suit='d', rank='2')
    
    def test_card_str(self):
        card = Card.objects.get(id=1)
        self.assertEqual(str(card), '2 of s')
    
    def test_card_compare_diff_suit_notrump_false(self):
        card1 = Card.objects.get(id=1) # 2 of spades
        card3 = Card.objects.get(id=3) # 2 of clubs
        self.assertFalse(card1.compare_rank(card3, 'h'))
    
    def test_card_compare_same_suit_notrump_true(self):
        card1 = Card.objects.get(id=1) # 2 of spades
        card2 = Card.objects.get(id=2) # 3 of spades
        self.assertTrue(card2.compare_rank(card1, 'h'))
    
    def test_card_compare_same_suit_notrump_false(self):
        card1 = Card.objects.get(id=1) # 2 of spades
        card2 = Card.objects.get(id=2) # 3 of spades
        self.assertFalse(card1.compare_rank(card2, 'h'))
        
    def test_card_compare_both_trump_true(self):
        card1 = Card.objects.get(id=1) # 2 of spades
        card2 = Card.objects.get(id=2) # 3 of spades
        self.assertTrue(card2.compare_rank(card1, 's'))
    
    def test_card_compare_both_trump_false(self):
        card1 = Card.objects.get(id=1) # 2 of spades
        card2 = Card.objects.get(id=2) # 3 of spades
        self.assertFalse(card1.compare_rank(card2, 's'))
        