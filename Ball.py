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
            # print(closest_player.player_id, ' is the closest to the ball')
            return self.set_player_possession(closest_player)
        else:
            # print('no one has ball')
            return self.set_player_possession()

    def reset_defendant_sensitivity_for_all_players(self):
        [p.reset_defendant_sensitivity() for p in self.players]

    def set_player_possession(self, player=None):
        if self.player_possessing is None:
            if player is not None:
                # if the previous player is none, assign the ball to the new player
                self.player_possessing = player
                self.player_possessing.possess_ball(True)
                self.reset_defendant_sensitivity_for_all_players()
                return False
            else:
                # if both are None, return nothing
                return False

        if player is None:
            # if ball was shot
            self.player_possessing.possess_ball(False)
            return False

        # if the player is the same, return nothing
        if player is self.player_possessing:
            self.player_possessing.possess_ball(True)
            self.reset_defendant_sensitivity_for_all_players()
            return False

        # if the new player is the opponent, remove the offside mark from the other team
        if player.team is not self.player_possessing.team:
            if player.acquires_ball():
                self.player_possessing.team.can_be_offside(False)
                # print(player.player_id, ' is NOW BALLLLLLLYYY')
            else:
                # print('wait for it')
                return False

        self.reset_defendant_sensitivity_for_all_players()
        self.player_possessing.possess_ball(False)
        self.player_possessing = player
        return self.player_possessing.possess_ball(True)
