# coding: utf8
import unittest

from posio.city import get_cities


class TestCity(unittest.TestCase):
    def test_get_random_city(self):
        # Check that a list of cities is returned
        cities = get_cities()
        self.assertTrue(len(cities) > 0)
