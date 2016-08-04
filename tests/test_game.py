# coding: utf8
import unittest

from posio.game import PosioGame


class TestGame(unittest.TestCase):
    def test_get_current_city(self):
        # Check that when a new turn is started the current city changes
        game = PosioGame()

        game.new_turn()
        city1 = game.get_current_city()
        
        game.new_turn()
        city2 = game.get_current_city()

        self.assertNotEqual(city1, city2)
