import math
import threading

import gui
from Coordinates import Coordinates
from Protocol import Protocol
import Settings
from Team import Team
from logic import Tag


class Ball:
    def __init__(self, location: Coordinates, players):
        self.location = location
        self.player_possessing = None

        self.speed = 0

        self.direction_ahmad = 0
        self.angle_ahmad = 0

        self.direction_arafeh = 0
        self.angle_arafeh = 0

        self.acceleration = 0
        self.distance_traveled_last_read_ahmad = 0
        self.distance_traveled_last_read_arafeh = 0

        self.players = players

    def reset(self):
        self.player_possessing = None
        self.speed = 0
        self.direction_ahmad = 0
        self.direction_arafeh = 0
        self.angle_ahmad = 0
        self.angle_arafeh = 0
        self.acceleration = 0
        self.distance_traveled_last_read_arafeh = 0
        self.distance_traveled_last_read_ahmad = 0

    def update_ball(self, tag: Tag):
        run_arafeh = False
        run_ahmad = False

        if tag.high_filtered_direction != 0.0:
            run_arafeh = True
            self.angle_arafeh = (tag.high_filtered_direction - self.direction_arafeh)
            self.direction_arafeh = tag.high_filtered_direction
            self.distance_traveled_last_read_arafeh = tag.high_filtered_direction

        if tag.direction != 0.0:
            run_ahmad = True
            self.angle_ahmad = (tag.direction - self.direction_ahmad)
            self.direction_ahmad = tag.direction
            self.distance_traveled_last_read_ahmad = tag.direction

        self.speed = tag.speed
        self.acceleration = tag.acceleration
        is_offside, offside_type = self.move_ball(tag, run_arafeh, run_ahmad)
        return is_offside, offside_type

    def move_ball(self, tag: Tag, run_ahmad, run_arafeh):
        self.location = tag.location

        # Assign ball to the closest player under threshold
        closest_player = None
        closest_distance = math.inf

        possession_radius = Settings.PLAYER_POSSESSION_PROXIMITY
        offside_type = 0
        # Change proximity if detected a curve in the ball direction

        for player in self.players:
            distance = self.location.get_ball_distance_with_player(player)
            if distance < closest_distance and distance < possession_radius:
                closest_player = player
                closest_distance = distance
                offside_type = 1

        if closest_player is None and run_ahmad:
            # print("ahmad", self.angle_ahmad)
            if abs(self.angle_ahmad) > Settings.DIRECTION_CURVE_THRESHOLD:
                possession_radius *= Settings.PLAYER_POSSESSION_PROXIMITY_MULTIPLIER
                for player in self.players:
                    distance = self.location.get_ball_distance_with_player(player)
                    if distance < closest_distance and distance < possession_radius:
                        closest_player = player
                        closest_distance = distance
                        offside_type = 2

        if closest_player is None and run_arafeh:
            # print("arafeh", self.angle_arafeh)
            if abs(self.angle_arafeh) > Settings.DIRECTION_CURVE_THRESHOLD:
                possession_radius *= Settings.PLAYER_POSSESSION_PROXIMITY_MULTIPLIER
                for player in self.players:
                    distance = self.location.get_ball_distance_with_player(player)
                    if distance < closest_distance and distance < possession_radius:
                        closest_player = player
                        closest_distance = distance
                        offside_type = 3

        if closest_player is not None:
            # print(closest_player.player_id, ' is the closest to the ball')
            return self.set_player_possession(closest_player), offside_type
        else:
            # print('no one has ball')
            return self.set_player_possession(), 0

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
