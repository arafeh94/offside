import tkinter
from random import randint
from time import sleep
from tkinter import *
from tkinter.ttk import *
from typing import List

from PIL import ImageTk, Image

from Coordinates import Coordinates
from DataGenerator import StreamData
from Protocol import Protocol
import Settings


class Util:
    @staticmethod
    def midpoint(x1, y1, x2, y2):
        return (x1 + x2) / 2, (y1 + y2) / 2


class Component:
    BALL_TAG = 0
    PLAYER_TAGS_START = 1
    PLAYER_TAGS_COUNT = 4

    def __init__(self, id, src, x, y, type, color="black"):
        self.ctx = Application.instance().ctx
        self.id = id
        self.src = ImageTk.PhotoImage(Image.open(src))
        self.x = x
        self.y = y
        self.color = color
        self.type = type
        self.events = {}
        self.component = None

    def draw(self):
        if self.id == Settings.BALL_TAG:
            self.component = self.ctx.create_image(self.x, self.y, anchor=tkinter.NW, image=self.src)
        else:
            self.component = self.ctx.create_text(self.x, self.y, anchor=tkinter.NW, text=str(self.id), fill=self.color, font=("Helvetica", 16))

    def change_text(self, text):
        self.ctx.itemconfigure(self.component, text=text)

    def loc(self):
        return self.ctx.coords(self.component)

    def set_location(self, x, y):
        self.x = x
        self.y = y
        self.update()

    def set_projected_location(self, x, y):
        self.x = Protocol.FIELD.X_START + (x * Protocol.FIELD.SCALE_X)
        # Protocol.FIELD.HEIGHT: because the anchors rotate counter clockwise during setup, so data received is swapped
        self.y = Protocol.FIELD.Y_START + Protocol.FIELD.HEIGHT - (y * Protocol.FIELD.SCALE_Y)
        self.update()

    def update(self):
        self.ctx.coords(self.component, self.x, self.y)

    def register_event(self, event_name: str, tag: str, callback):
        if event_name not in self.events:
            self.events[event_name] = {}
        self.events[event_name][tag] = callback

    def unregister_event(self, event_name, tag):
        if event_name in self.events and tag in self.events[event_name]:
            del self.events[event_name][tag]

    def broadcast(self, event_name, params):
        if event_name not in self.events:
            return
        for callback in self.events[event_name].values():
            callback(params)


class Player(Component):
    EVENT_PLAYER_MOVE = "EVENT_PLAYER_MOVE"
    EVENT_PLAYER_SHOOT = "EVENT_PLAYER_SHOOT"

    def __init__(self, id, team, x, y, color="white", tags=None, has_control=False, speed=20):
        super(Player, self).__init__(id, "assets/home.png" if team == 0 else "assets/visitor.png", x, y, 'player', color)
        if tags is None:
            tags = []
        self.has_control = has_control
        self.speed_x = 0
        self.speed_y = 0
        self.speed = speed
        self.tags = tags

    def has_tag(self, tag):
        for t in self.tags:
            if t == tag:
                return True
        return False

    def set_control(self, has_control):
        self.has_control = has_control

    def key_move(self, key):
        if self.has_control:
            if key == 'down':
                self.speed_x = 0
                self.speed_y = self.speed
            elif key == 'up':
                self.speed_x = 0
                self.speed_y = -self.speed
            elif key == 'left':
                self.speed_x = -self.speed
                self.speed_y = 0
            elif key == 'right':
                self.speed_x = self.speed
                self.speed_y = 0

            self.ctx.move(self.component, self.speed_x, self.speed_y)
            self.broadcast(Player.EVENT_PLAYER_MOVE, self)

    def shoot(self, event, tag):
        self.broadcast(Player.EVENT_PLAYER_SHOOT, self)


# noinspection PyTypeChecker
class Ball(Component):
    LOCATION_MODIFIER_X = 0
    LOCATION_MODIFIER_Y = 20
    EVENT_BALL_MOVED = 'EVENT_BALL_MOVED'
    EVENT_BALL_SHOOT = 'EVENT_BALL_SHOOT'

    def __init__(self,id,x,y):
        super(Ball, self).__init__(id, "assets/ball.png", x, y, 'ball')
        self.attached: Player = None

    def attach(self, player: Player):
        if self.attached is not None:
            self.attached.set_control(False)
        self.attached = player
        self.attached.set_control(True)
        # first half movement
        midpoint = Util.midpoint(player.loc()[0], player.loc()[1], self.loc()[0], self.loc()[1])
        self.set_location(midpoint[0] + Ball.LOCATION_MODIFIER_X, midpoint[1] + Ball.LOCATION_MODIFIER_Y)
        self.broadcast(Ball.EVENT_BALL_SHOOT, self)

        # complete movement
        self.set_location(player.loc()[0] + Ball.LOCATION_MODIFIER_X, player.loc()[1] + Ball.LOCATION_MODIFIER_Y)
        self.broadcast(Ball.EVENT_BALL_SHOOT, self)

        # attach ball to player
        self.attached.register_event(Player.EVENT_PLAYER_MOVE, 'ball_move', self.event_player_moved)

    def event_player_moved(self, player: Player):
        self.set_location(player.loc()[0] + Ball.LOCATION_MODIFIER_X, player.loc()[1] + Ball.LOCATION_MODIFIER_Y)
        self.broadcast(Ball.EVENT_BALL_MOVED, self)

    def shoot(self):
        self.ctx.move(self.component, 0, 150)
        self.broadcast(Ball.EVENT_BALL_SHOOT, self)
        self.broadcast(Ball.EVENT_BALL_MOVED, self)


# noinspection PyTypeChecker
class Application:
    _app = None

    @staticmethod
    def instance():
        if Application._app is None:
            Application._app = Application()
        return Application._app

    def __init__(self):
        self.root = tkinter.Tk()
        self.ctx = tkinter.Canvas(self.root, bg="white", height=Protocol.FIELD.HEIGHT+Protocol.FIELD.Y_START*2,
                                  width=Protocol.FIELD.WIDTH+Protocol.FIELD.X_START*2)
        self.players: List[Player] = []
        self.ball: Ball = None
        # self.can_move: bool = True

    def draw_pitch(self, image):
        self.ctx.create_image(0, 0, anchor=tkinter.NW, image=image)

    def add_player(self, player: Player):
        self.players.append(player)
        player.draw()

    def set_ball(self, ball: Ball):
        self.ball = ball
        ball.draw()

    def get_ball(self):
        return self.ball

    def place_all(self):
        for player in self.players:
            player.set_projected_location(player.x, player.y)
        self.ball.set_projected_location(self.ball.x, self.ball.y)

    def loop(self):
        # self.bind_movement_keys()
        # self.bind_number_keys()
        self.ctx.pack()
        self.root.mainloop()
