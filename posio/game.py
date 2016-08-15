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
        self.players = {}
        self.answers = []
        self.turn_number = 0

    def add_player(self, player_sid, player_name):
        self.players[player_sid] = {
            'name': player_name,
            'scores': {}
        }

    def remove_player(self, player_sid):
        self.players.pop(player_sid, None)

    def start_new_turn(self):
        # Reset answers for this turn
        self.answers = []

        # Update turn number
        self.turn_number += 1

    def store_answer(self, player_sid, latitude, longitude):
        # Get the distance between player answer and correct answer
        current_city = self.get_current_city()
        distance = self.plane_distance(current_city['latitude'], current_city['longitude'], latitude, longitude)

        score = self.score(distance)

        self.answers.append({
            'sid': player_sid,
            'latitude': latitude,
            'longitude': longitude,
            'score': score,
            'distance': distance
        })

        self.get_player(player_sid)['scores'][self.turn_number] = score

    def get_current_city(self):
        # Return a different city for each turn
        return self.cities[self.turn_number % len(self.cities)]

    def get_ranked_answers(self):
        return sorted(self.answers, key=lambda answer: answer['score'], reverse=True)

    def get_ranked_scores(self):
        scores_by_player = {}

        for player_sid in self.players:
            # Compute the player score for the last 20 turns
            score = 0

            for previous_turn in range(self.turn_number - 19, self.turn_number + 1):
                score += self.players[player_sid]['scores'].get(previous_turn, 0)

            # Store the score
            scores_by_player[player_sid] = score

        ranked_scores = [{'sid': sid, 'score': scores_by_player[sid]} for sid in
                         sorted(scores_by_player, key=lambda sid: scores_by_player[sid], reverse=True)]

        return ranked_scores

    def score(self, distance):
        # Convert distance to a score
        score = round(self.score_max_distance - distance)

        return max(0, score)

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

    def get_player(self, player_sid):
        if player_sid not in self.players:
            self.add_player(player_sid, 'Unknown')
        return self.players[player_sid]
