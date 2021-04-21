from time import sleep

import Settings
import utils
from Coordinates import Coordinates
from Protocol import Protocol
from Team import Team
from logic import Tag


class Player:

    def __init__(self, player_id, team: Team):
        self.team = team
        self.player_id = player_id
        self.team.add_player(self)
        self.is_possessing_ball = False
        self.is_in_offside_position = False
        self.is_offside_alert = False
        self.tags = {}
        self.player_gui = None

        self.ball_touch_sensitivity_in_case_defending = Settings.DEFENDANT_BALL_TOUCH_SENSITIVITY

    def acquires_ball(self):
        self.ball_touch_sensitivity_in_case_defending -= 1
        # print(self.player_id, ' SENSITIVITY ***************** ', self.ball_touch_sensitivity_in_case_defending)
        return self.ball_touch_sensitivity_in_case_defending <= 0

    def reset_defendant_sensitivity(self):
        self.ball_touch_sensitivity_in_case_defending = Settings.DEFENDANT_BALL_TOUCH_SENSITIVITY

    def get_player_id(self):
        return self.player_id

    def get_player_locations(self):
        return [t.location for t in utils.as_list(self.tags)]

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

    def init_tag(self, tag: Tag):
        self.tags[tag.tag_id] = tag

    def set_tag(self, tag: Tag):
        if tag.tag_id not in [t.tag_id for t in utils.as_list(self.tags)]:
            return False
        self.tags[tag.tag_id] = tag
        return True

    def set_team(self, team):
        self.team = team

    def set_is_possessing_ball(self, value):
        self.is_possessing_ball = value

    def set_is_in_offside_position(self, value):
        self.is_in_offside_position = value
        if self.is_in_offside_position:
            pass
            # print(str(self.player_id) + ' is exposed to a potential offside')

    def set_is_offside_alert(self, value):
        self.is_offside_alert = value

    def set_player_gui(self, gui):
        self.player_gui = gui

    #
    # def set_player_location(self, tag, location):
    #     index = self.tags.index(tag)
    #     self.locations[index] = location

    #
    # def set_player_location_with_duplicate(self, tag, location):
    #     index = 0
    #     for t in self.tags:
    #         if t == tag:
    #             self.locations[index] = location
    #         index += 1
    #
    # def has_tag(self, tag):
    #     for t in self.tags:
    #         if str(t) == tag:
    #             return True
    #     return False

    def change_display(self):
        if self.is_offside_alert:
            self.player_gui.change_text(str(self.player_id) + " OFFSIDE")
        elif self.is_in_offside_position:
            self.player_gui.change_text(str(self.player_id) + " !!")
        elif self.is_possessing_ball:
            self.player_gui.change_text(str(self.player_id) + " *****")
        else:
            self.player_gui.change_text(str(self.player_id))

    def reset(self):
        self.set_is_possessing_ball(False)
        self.set_is_in_offside_position(False)
        self.set_is_offside_alert(False)
        self.change_display()

    def possess_ball(self, is_possessing_ball):
        if is_possessing_ball:
            # if he already has the ball, return
            if self.is_possessing_ball:
                return False

            # if he doesnt have the ball and received it from another team mate, and is offside -> alert
            self.set_is_possessing_ball(True)
            if self.is_in_offside_position:
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
        pass
        # print(str(self.player_id) + ' is offside!!')

    def is_ahead_of(self, player2):
        if self.team.side == Protocol.SIDE_TOP:
            return self.get_front_location(Team.get_opponent(self.team.side)).y < player2.get_front_location(
                Team.get_opponent(self.team.side)).y
        else:
            return self.get_front_location(Team.get_opponent(self.team.side)).y > player2.get_front_location(
                Team.get_opponent(self.team.side)).y

    def get_front_location(self, towards_side):
        sorted_locations = sorted(self.get_player_locations(), key=lambda loc: loc.y, reverse=True)
        if towards_side == Protocol.SIDE_TOP:
            return sorted_locations[0]
        else:
            return sorted_locations[-1]

    def get_back_location(self, towards_side):
        sorted_locations = sorted(self.get_player_locations(), key=lambda loc: loc.y, reverse=False)
        if towards_side == Protocol.SIDE_TOP:
            return sorted_locations[0]
        else:
            return sorted_locations[-1]

    def get_average_location(self):
        return Coordinates(
            sum(loc.x for loc in self.get_player_locations()) / len(self.get_player_locations()),
            sum(loc.y for loc in self.get_player_locations()) / len(self.get_player_locations()),
            sum(loc.z for loc in self.get_player_locations()) / len(self.get_player_locations())
        )

    def is_before_half_line(self):
        if self.team.side == Protocol.SIDE_TOP:
            return self.get_back_location(self.team.side).y > Protocol.FIELD.HALF_FIELD
        else:
            return self.get_back_location(self.team.side).y < Protocol.FIELD.HALF_FIELD

    def speed(self):
        return utils.as_list(self.tags)[0].speed

    def direction(self):
        return utils.as_list(self.tags)[0].direction

    def acceleration(self):
        return utils.as_list(self.tags)[0].acceleration


