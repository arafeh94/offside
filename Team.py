from Protocol import Protocol


class Team:
    class_counter = 0

    def __init__(self, name, color, side):
        self.name = name
        self.color = color
        self.side = side
        self.id = Team.class_counter
        self.players = []
        Team.class_counter += 1

    def add_player(self, player):
        self.players.append(player)

    def possessing_ball(self):
        for x in self.players:
            if x.is_possessing_ball:
                return True
        return False

    def can_be_offside(self, value):
        for x in self.players:
            x.is_in_offside_position = value

    def get_second_last_defendant(self):
        sorted_defendants = sorted(self.players, key=lambda x: x.get_back_location(self.side).y, reverse=False)
        if self.side == Protocol.SIDE_TOP:
            return sorted_defendants[-2]
        else:
            return sorted_defendants[1]

    def set_offside_attribute(self, team_2):
        second_last_def = team_2.get_second_last_defendant()

        player_possessing_ball = None
        for y in self.players:
            if y.is_possessing_ball:
                player_possessing_ball = y

        for y in self.players:
            if not y.is_possessing_ball:
                # print(y.location)
                # y is ahead of player whos possessing ball
                if player_possessing_ball is not None:
                    ahead_of_player_with_ball = y.is_ahead_of(player_possessing_ball)
                    y.set_is_in_offside_position(
                        y.is_ahead_of(second_last_def) and not y.is_before_half_line() and ahead_of_player_with_ball)
                else:
                    y.set_is_in_offside_position(y.is_ahead_of(second_last_def) and not y.is_before_half_line())
