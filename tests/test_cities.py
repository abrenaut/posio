# coding: utf8
import unittest

from posio.city import get_random_city


class TestNetworkWS(unittest.TestCase):
    def test_get_random_city(self):
        # Check that a random city is returned
        city = get_random_city()
        self.assertIsNotNone(city)
