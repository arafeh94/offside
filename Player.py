from time import sleep

from Ball import Ball
from Coordinates import Coordinates
from Protocol import Protocol
from Team import Team


class Player:

    def __init__(self, player_id, team: Team):
        self.team = team
        self.player_id = player_id
        self.team.add_player(self)
        self.is_possessing_ball = False
        self.is_in_offside_position = False
        self.is_offside_alert = False

        self.speed = 0
        self.direction = 0

        self.locations = []
        self.tags = []
        self.player_gui = None

    def set_speed(self, speed):
        self.speed = speed

    def set_direction(self, direction):
        self.speed = direction

    def get_speed(self):
        return self.speed

    def get_direction(self):
        return self.direction

    def get_player_id(self):
        return self.player_id

    def get_player_locations(self):
        return self.locations

    def get_tags(self):
        return self.tags

    def get_team(self):
        return self.team

    def get_is_possessing_ball(self):
        return self.is_possessing_ball

    def get_is_in_offside_position(self):
        return self.is_in_offside_position

    def get_is_offside_alert(self):
        return self.is_offside_alert

    def get_player_gui(self):
        return self.player_gui

    def set_player_id(self, player_id):
        self.player_id = player_id

    def set_player_locations(self, locations):
        self.locations = locations

    def set_player_tags(self, tags):
        self.tags = tags

    def add_tag(self, tag, location=None):
        self.tags.append(tag)
        if location is None:
            self.locations.append(Coordinates(0, 0, 0))
        else:
            self.locations.append(location)

    def set_team(self, team):
        self.team = team

    def set_is_possessing_ball(self, value):
        self.is_possessing_ball = value

    def set_is_in_offside_position(self, value):
        self.is_in_offside_position = value
        if self.is_in_offside_position:
            print(str(self.player_id) + ' is exposed to a potential offside')

    def set_is_offside_alert(self, value):
        self.is_offside_alert = value

    def set_player_gui(self, gui):
        self.player_gui = gui

    def set_player_location(self, tag, location):
        index = self.tags.index(tag)
        self.locations[index] = location

    def set_player_location_with_duplicate(self, tag, location):
        index = 0
        for t in self.tags:
            if t == tag:
                self.locations[index] = location
            index += 1

    def has_tag(self, tag):
        for t in self.tags:
            if t == tag:
                return True
        return False

    def change_display(self):
        if self.is_offside_alert:
            self.player_gui.change_text(str(self.player_id) + " OFFSIDE")
        elif self.is_in_offside_position:
            self.player_gui.change_text(str(self.player_id) + " !!")
        elif self.is_possessing_ball:
            self.player_gui.change_text(str(self.player_id) + " *")
        else:
            self.player_gui.change_text(str(self.player_id))

    def reset(self):
        self.set_is_possessing_ball(False)
        self.set_is_in_offside_position(False)
        self.set_is_offside_alert(False)
        self.set_speed(0)
        self.set_direction(0)
        self.change_display()

    def possess_ball(self, ball: Ball, is_possessing_ball):
        if is_possessing_ball:
            # if he already has the ball, return
            if self.is_possessing_ball:
                return False

            # if he doesnt have the ball and received it from another team mate, and is offside -> alert
            self.set_is_possessing_ball(True)
            if self.is_in_offside_position and self.is_same_team(ball.last_player):
                self.set_is_offside_alert(True)
                self.offside_player_alert()
                return True
        else:
            self.set_is_possessing_ball(False)
        return False

    def is_same_team(self, player):
        if player is None:
            return False
        return self.team.side == player.team.side

    def offside_player_alert(self):
        print(str(self.player_id) + ' is offside!!')

    def is_ahead_of(self, player2):
        if self.team.side == Protocol.SIDE_HOME:
            return self.get_front_location(self.team.side).y > player2.get_front_location(self.team.side).y
        else:
            return self.get_front_location(self.team.side).y < player2.get_front_location(self.team.side).y

    def get_front_location(self, towards_side):
        sorted_locations = sorted(self.locations, key=lambda loc: loc.y, reverse=False)
        if towards_side == Protocol.SIDE_HOME:
            return sorted_locations[0]
        else:
            return sorted_locations[-1]

    def get_back_location(self, towards_side):
        sorted_locations = sorted(self.locations, key=lambda loc: loc.y, reverse=True)
        if towards_side == Protocol.SIDE_HOME:
            return sorted_locations[0]
        else:
            return sorted_locations[-1]

    def get_average_location(self):
        return Coordinates(
            sum(loc.x for loc in self.locations) / len(self.locations),
            sum(loc.y for loc in self.locations) / len(self.locations),
            sum(loc.z for loc in self.locations) / len(self.locations)
        )

    def is_before_half_line(self):
        if self.team.side == Protocol.SIDE_HOME:
            return self.get_back_location(self.team.side).y < Protocol.FIELD.HALF_FIELD
        else:
            return self.get_back_location(self.team.side).y > Protocol.FIELD.HALF_FIELD
