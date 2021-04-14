from Coordinates import Coordinates


class Tag:
    def __init__(self, tag_id, timestamp=0, coordinates=Coordinates(0, 0, 0), speed=0, direction=0, acceleration=0):
        self.tag_id = tag_id
        self.location = coordinates
        self.speed = speed
        self.direction = direction
        self.acceleration = acceleration
        self.timestamp = timestamp
