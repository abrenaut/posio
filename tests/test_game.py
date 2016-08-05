# coding: utf8
import unittest

from posio.game import PosioGame


class TestGame(unittest.TestCase):
    def test_get_current_city(self):
        # Check that when a new turn is started the current city changes
        game = PosioGame()

        game.new_turn()
        city1 = game.current_city()

        game.new_turn()
        city2 = game.current_city()

        self.assertNotEqual(city1, city2)

    def test_get_cities(self):
        # Check that a list of cities is returned
        game = PosioGame()
        cities = game.get_cities()
        self.assertTrue(len(cities) > 0)

    def test_distance(self):
        # Test the distance function
        game = PosioGame()

        # Exact match
        distance = game.plane_distance(48.3515609, -1.204625999999962, 48.3515609, -1.204625999999962)
        self.assertEquals(distance, 0)

        # 6 km away
        distance = game.plane_distance(48.3515609, -1.204625999999962, 48.370431, -1.151591000000053)
        self.assertEquals(round(distance), 6)

        # More than a thousand km away
        distance = game.plane_distance(48.3515609, -1.204625999999962, 40.7127837, -74.00594130000002)
        self.assertEquals(round(distance), 8149)

    def test_score(self):
        # Test the scoring function
        game = PosioGame()

        # Exact match
        score = game.score(0)
        self.assertEquals(score, 1000)

        # 6 km away
        score = game.score(6)
        self.assertEquals(score, 994)

        # More than a thousand km away
        score = game.score(1000)
        self.assertEquals(score, 0)

    def test_ranked_answer(self):
        # Test the ranking function
        game = PosioGame()

        # Mock the get_current_city function to always return the same city
        game.current_city = lambda: {
            'latitude': 48.3515609,
            'longitude': -1.204625999999962
        }

        game.store_answer('a', 48.3515609, -1.204625999999962)
        game.store_answer('b', 48.370431, -1.151591000000053)
        game.store_answer('c', 40.7127837, -74.00594130000002)

        ranked_answers = game.ranked_answers()

        self.assertEquals(ranked_answers[0]['uuid'], 'a')
        self.assertEquals(ranked_answers[1]['uuid'], 'b')
        self.assertEquals(ranked_answers[2]['uuid'], 'c')
