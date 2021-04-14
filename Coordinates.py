import math
import random
from random import randint

from Protocol import Protocol


class Coordinates:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get_distance(self, location2):
        return (((self.x - location2.x) ** 2) + ((self.y - location2.y) ** 2) + ((self.z - location2.z) ** 2)) ** 0.5

    def get_ball_distance_with_player(self, player):
        min_distance = math.inf
        for tag in player.get_player_locations():
            distance = self.get_distance(tag)
            print(player.player_id, ' - ', distance)
            if distance < min_distance:
                min_distance = distance
        print(min_distance)
        return min_distance

    @staticmethod
    def generate_random_location():
        return Coordinates(random.uniform(0, Protocol.FIELD.REAL_WIDTH), random.uniform(0, Protocol.FIELD.REAL_HEIGHT), 0)

    @staticmethod
    def generate_random_location2(location):
        return Coordinates(random.uniform(location.x - 8, location.x + 8), random.uniform(location.y - 8, location.y + 8), 0)

    def __str__(self):
        output = ""
        for _, var in vars(self).items():
            output += str(var) + '\n'
        return output
