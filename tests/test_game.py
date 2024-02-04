# coding: utf8
import unittest

from posio.game import Game


class TestGame(unittest.TestCase):
    def test_get_current_city(self):
        # Check that when a new turn is started the current city changes
        game = Game(1000, 10)

        game.start_new_turn()
        city1 = game.get_current_city()

        game.start_new_turn()
        city2 = game.get_current_city()

        self.assertNotEqual(city1, city2)

    def test_get_cities(self):
        # Check that a list of cities is returned
        cities = Game.get_cities()
        self.assertTrue(len(cities) > 0)

    def test_distance(self):
        # Test the distance function
        game = Game(1000, 10)

        # Exact match
        distance = game.plane_distance(48.3515609, -1.204625999999962, 48.3515609, -1.204625999999962)
        self.assertEqual(distance, 0)

        # 6 km away
        distance = game.plane_distance(48.3515609, -1.204625999999962, 48.370431, -1.151591000000053)
        self.assertEqual(round(distance), 6)

        # More than a thousand km away
        distance = game.plane_distance(48.3515609, -1.204625999999962, 40.7127837, -74.00594130000002)
        self.assertEqual(round(distance), 8149)

    def test_score(self):
        # Test the scoring function
        game = Game(1000, 10)

        # Exact match, really fast
        score = game.score(0)
        self.assertEqual(score, 1000)

        # Exact match but really slow
        score = game.score(0)
        self.assertEqual(score, 1000)

        # 6 km away but slow
        score = game.score(6)
        self.assertEqual(score, 994)

        # More than a thousand km away
        score = game.score(1000)
        self.assertEqual(score, 0)

    def test_get_current_turn_ranks(self):
        # Test the ranking function
        game = Game(1000, 10)

        # Mock the get_current_city function to always return the same city
        game.get_current_city = lambda: {
            'latitude': 48.3515609,
            'longitude': -1.204625999999962
        }

        game.add_player('a', 'a')
        game.add_player('b', 'b')
        game.add_player('c', 'c')

        game.store_answer('a', 48.3515609, -1.204625999999962)
        game.store_answer('b', 48.370431, -1.151591000000053)
        game.store_answer('c', 40.7127837, -74.00594130000002)

        game.end_current_turn()

        ranked_players = game.get_current_turn_ranks()

        self.assertEqual(ranked_players[0].sid, 'a')
        self.assertEqual(ranked_players[1].sid, 'b')
        self.assertEqual(ranked_players[2].sid, 'c')

    def test_get_ranked_scores(self):
        # Test the ranking function
        game = Game(1000, 20)

        # Mock the get_current_city function to always return the same city
        game.get_current_city = lambda: {
            'latitude': 48.3515609,
            'longitude': -1.204625999999962
        }

        game.add_player('a', 'a')
        game.add_player('b', 'b')
        game.add_player('c', 'c')

        # Always return the correct answer for player a, a close answer for c and an answer far away for b
        for i in range(0, 30):
            game.start_new_turn()
            game.store_answer('a', 48.3515609, -1.204625999999962)
            game.store_answer('b', 0, 0)
            game.store_answer('c', 48.370431, -1.151591000000053)
            game.end_current_turn()

        self.assertEqual(game.get_ranked_scores()[0]['player'].sid, 'a')
        self.assertEqual(game.get_ranked_scores()[1]['player'].sid, 'c')
        self.assertEqual(game.get_ranked_scores()[2]['player'].sid, 'b')
        # Max score shouldn't be higher than 20000 because we limit to 20 turns to compute score
        self.assertEqual(game.get_ranked_scores()[0]['score'], 20000)

