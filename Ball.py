import math

import gui
from Coordinates import Coordinates
from Protocol import Protocol
import Settings
from Team import Team


class Ball:
    def __init__(self, location: Coordinates, players):
        self.location = location
        self.player_possessing = None
        self.last_player = None

        self.speed = 0
        self.direction = 0

        self.players = players

    def set_speed(self, speed):
        self.speed = speed

    def set_direction(self, direction):
        self.speed = direction

    def get_speed(self):
        return self.speed

    def get_direction(self):
        return self.direction

    def reset(self):
        self.player_possessing = None
        self.last_player = None
        self.set_speed(0)
        self.set_direction(0)

    def move_ball(self, location: Coordinates):
        self.location = location

        # Assign ball to the closest player under threshold
        closest_player = None
        closest_distance = math.inf
        for player in self.players:
            distance = self.location.get_ball_distance_with_player(player)
            if distance < closest_distance and distance < Settings.PLAYER_POSSESSION_PROXIMITY:
                closest_player = player
                closest_distance = distance
        if closest_player is not None:
            print(closest_player.player_id, ' has ball')
            return self.set_player_possession(closest_player)

    def set_player_possession(self, player):
        # returns true if the possession is offside
        if self.player_possessing is None:
            self.player_possessing = player
            player.possess_ball(self, True)
            return False

        self.last_player = self.player_possessing
        if self.last_player.team is not player.team:
            self.last_player.team.can_be_offside(False)
        self.last_player.possess_ball(self, False)

        self.player_possessing = player
        return player.possess_ball(self, True)
