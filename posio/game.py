# -*- coding: utf-8 -*-

import sqlite3
import os
from math import sqrt, pi

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

# Earth ellipsoid equator length in meters
EARTH_EQUATOR = 6378137.0

# Convert degrees to kilometres
DISTANCE_PER_DEGREE = (2 * pi * EARTH_EQUATOR) / (360 * 1000)


class PosioGame:
    def __init__(self, game_id, score_max_distance):
        self.game_id = game_id
        self.score_max_distance = score_max_distance
        self.cities = self.get_cities()
        self.answers = []
        self.turn_number = 0
        self.scores_by_turn = {self.turn_number: {}}

    def current_city(self):
        # Return a different city for each turn
        return self.cities[self.turn_number % len(self.cities)]

    def new_turn(self):
        # Reset answers
        self.answers = []

        # Update turn number
        self.turn_number += 1

        # Create the dictionary where this turn scores will be stored
        self.scores_by_turn[self.turn_number] = {}

        # Only keep the scores for the last 20 turns
        for turn in [turn for turn in self.scores_by_turn if turn <= self.turn_number - 20]:
            self.scores_by_turn.pop(turn)

    def store_answer(self, uuid, latitude, longitude):
        # Get the distance between user answer and correct answer
        current_city = self.current_city()
        distance = self.plane_distance(current_city['latitude'], current_city['longitude'], latitude, longitude)

        score = self.score(distance)

        self.scores_by_turn[self.turn_number][uuid] = score

        self.answers.append({
            'uuid': uuid,
            'lat': latitude,
            'lng': longitude,
            'score': score,
            'distance': distance
        })

    def ranked_answers(self):
        return sorted(self.answers, key=lambda answer: answer['score'], reverse=True)

    def score(self, distance):
        # Convert distance to a score
        score = round(self.score_max_distance - distance)

        return max(0, score)

    def get_ranked_scores(self):
        scores_by_user = {}

        for turn, scores in self.scores_by_turn.iteritems():
            for uuid, score in scores.iteritems():
                scores_by_user[uuid] = scores_by_user.get(uuid, 0) + score

        ranked_scores = [{'uuid': uuid, 'score': scores_by_user[uuid]} for uuid in
                         sorted(scores_by_user, key=lambda uuid: scores_by_user[uuid], reverse=True)]

        return ranked_scores

    @staticmethod
    def get_cities():
        # Connect to the city database
        conn = sqlite3.connect(os.path.join(DIR_PATH, '../data/cities.db'))

        # Select every cities in random order
        c = conn.cursor()

        cities = []
        for city_data in c.execute('SELECT name, country, latitude, longitude FROM cities ORDER BY RANDOM()'):
            cities.append({
                'name': city_data[0],
                'country': city_data[1],
                'latitude': city_data[2],
                'longitude': city_data[3]
            })

        # Close connection
        conn.close()

        return cities

    @staticmethod
    def plane_distance(latitude1, longitude1, latitude2, longitude2):
        # Calculates distance as points on a plane
        px = longitude2 - longitude1
        py = latitude2 - latitude1
        return sqrt(px * px + py * py) * DISTANCE_PER_DEGREE
