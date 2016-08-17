# -*- coding: utf-8 -*-

import sqlite3
import os
from math import sqrt, pi

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

# Earth ellipsoid equator length in meters
EARTH_EQUATOR = 6378137.0

# Convert degrees to kilometres
DISTANCE_PER_DEGREE = (2 * pi * EARTH_EQUATOR) / (360 * 1000)


class Game:
    def __init__(self, game_id, score_max_distance=1000, max_response_time=5, leaderboard_answer_count=20,
                 between_turns_duration=3):
        """
        :param game_id:
        :param score_max_distance: The max distance above which player scores will be null
        :param leaderboard_answer_count: How many answers are used to compute user scores in the leaderboard
        :param max_response_time: The time given to a player to answer a question
        :param between_turns_duration: The time between two turns
        :return:
        """
        self.game_id = game_id
        self.score_max_distance = score_max_distance
        self.leaderboard_answer_count = leaderboard_answer_count
        self.max_response_time = max_response_time
        self.between_turns_duration = between_turns_duration
        self.cities = self.get_cities()
        self.players = []
        self.answers = []
        self.turn_number = 0

    def add_player(self, player_sid, player_name):
        self.players.append(Player(player_sid, player_name))

    def remove_player(self, player_sid):
        # Get the player corresponding to the given sid and remove it if it is found
        player = self.get_player(player_sid)

        if player:
            self.players.remove(player)

    def start_new_turn(self):
        # Reset answers for this turn
        self.answers = []

        # Update turn number
        self.turn_number += 1

    def get_current_city(self):
        # Return a different city for each turn
        return self.cities[self.turn_number % len(self.cities)]

    def store_answer(self, player_sid, latitude, longitude, answer_duration):
        # Get the player corresponding to the given sid
        player = self.get_player(player_sid)

        if player:
            # Get the distance between player answer and correct answer
            current_city = self.get_current_city()
            distance = self.plane_distance(current_city['latitude'], current_city['longitude'], latitude, longitude)

            # Compute player score for this answer
            score = self.score(distance, answer_duration)

            # Store player answer
            answer = Answer(latitude, longitude, score, distance, answer_duration)
            player.add_answer(self.turn_number, answer)

    def get_current_turn_ranks(self):
        # Get players who gave an answer this turn
        current_turn_players = [player for player in self.players if player.has_answered(self.turn_number)]

        # Sort players based on their scores on this turn
        ranked_players = sorted(current_turn_players,
                                key=lambda current_turn_player: current_turn_player.answers[self.turn_number].score,
                                reverse=True)

        return ranked_players

    def get_ranked_scores(self):
        # Get scores for each players
        scores_by_player = {player: player.get_score(self.turn_number - self.leaderboard_answer_count, self.turn_number)
                            for player in self.players}

        # Rank the scores
        ranked_scores = [{'player': player, 'score': scores_by_player[player]} for player in
                         sorted(self.players, key=lambda player: scores_by_player[player], reverse=True)]

        return ranked_scores

    def score(self, distance, answer_duration):
        # Convert distance to a score
        score = max(0, round(self.score_max_distance - distance))

        # If user is not too far away, take into account response time
        if score > 0:
            score += round((1 - (answer_duration / float((self.max_response_time * 1000)))) * self.score_max_distance / 2)

        return score

    def get_player(self, player_sid):
        player = None

        for existing_player in self.players:
            if existing_player.sid == player_sid:
                player = existing_player
                break

        return player

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


class Player:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
        self.answers = {}

    def add_answer(self, turn, answer):
        self.answers[turn] = answer

    def has_answered(self, turn):
        return turn in self.answers

    def get_score(self, start_turn, end_turn):
        # Compute the player score for the turns between start_turn and end_turn
        return sum(answer.score for turn, answer in self.answers.iteritems() if start_turn < turn <= end_turn)

    def __hash__(self):
        return hash(self.sid)

    def __eq__(self, other):
        return self.sid == other.sid


class Answer:
    def __init__(self, latitude, longitude, score, distance, answer_duration):
        self.latitude = latitude
        self.longitude = longitude
        self.score = score
        self.distance = distance
        self.answer_duration = answer_duration
