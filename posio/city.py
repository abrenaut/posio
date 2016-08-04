# -*- coding: utf-8 -*-
import sqlite3
import os

dir_path = os.path.dirname(os.path.abspath(__file__))


class City:
    def __init__(self, name, country, lat, lng):
        self.name = name
        self.country = country
        self.lat = lat
        self.lng = lng


def get_cities():
    # Connect to the city database
    conn = sqlite3.connect(os.path.join(dir_path, '../data/cities.db'))

    # Select every cities in random order
    c = conn.cursor()

    cities = []
    for city_data in c.execute('SELECT * FROM cities ORDER BY RANDOM()'):
        # Create City objects
        cities.append(City(city_data[0], city_data[1], city_data[2], city_data[3]))

    # Close connection
    conn.close()

    return cities
