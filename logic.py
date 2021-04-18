import utils
from Coordinates import Coordinates


class Tag:
    def __init__(self, tag_id, timestamp=0, coordinates=Coordinates(0, 0, 0), speed=0, direction=0, acceleration=0,
                 distance=0, high_filtered_speed=0, high_filtered_direction=0, high_filtered_acceleration=0,
                 high_filtered_distance=0):
        self.tag_id = tag_id
        self.location = coordinates
        self.speed = speed
        self.direction = direction
        self.acceleration = acceleration
        self.distance = distance
        self.timestamp = timestamp
        self.high_filtered_speed = high_filtered_speed
        self.high_filtered_direction = high_filtered_direction
        self.high_filtered_acceleration = high_filtered_acceleration
        self.high_filtered_distance = high_filtered_distance

    def __repr__(self):
        return utils.csv((self.tag_id, self.speed, self.direction, self.acceleration))
