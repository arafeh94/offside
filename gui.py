import math
import random
import tkinter
from abc import abstractmethod
from threading import Thread
from tkinter import *
from tkinter import ttk
from typing import List, NewType
from PIL import ImageTk, Image

import utils
from Ball import Ball
from Protocol import Protocol
import Settings
from logic import Tag


class Util:
    @staticmethod
    def midpoint(x1, y1, x2, y2):
        return (x1 + x2) / 2, (y1 + y2) / 2

    @staticmethod
    def create_circle(x, y, r, canvas):  # center coordinates, radius
        x0 = (x - r)
        y0 = (y - r)
        x1 = (x + r)
        y1 = (y + r)
        return canvas.create_oval(x0, y0, x1, y1, outline="#DDD", width=2)


class Component:
    def __init__(self, cid, x, y, ctag=None):
        self.ctx = Application.instance().ctx
        self.cid = cid
        self.x = x
        self.y = y
        self.ctag = ctag
        self.events = {}
        self.component = None

    @abstractmethod
    def draw(self):
        pass

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


class TextComponent(Component):

    def __init__(self, cid, content, color, x, y, font=("Helvetica", 16), ctag=None):
        super().__init__(cid, x, y, ctag)
        self.content = str(content)
        self.color = color
        self.font = font

    def draw(self):
        self.component = self.ctx.create_text(self.x, self.y, anchor=tkinter.NW,
                                              text=self.content, fill=self.color, font=self.font)

    def change_text(self, content):
        self.ctx.itemconfigure(self.component, text=content)


class ImageComponent(Component):
    def __init__(self, cid, src, x, y, ctag=None):
        super().__init__(cid, x, y, ctag)
        self.src = ImageTk.PhotoImage(Image.open(src))

    def draw(self):
        self.component = self.ctx.create_image(self.x, self.y, anchor=tkinter.NW, image=self.src)


class Player(TextComponent):
    colors = ['silver', 'silver', 'pink', 'cyan', 'grey', 'orange']

    def __init__(self, cid: str, logic_player):
        super(Player, self). \
            __init__(cid, cid, logic_player.team.color,
                     utils.first(logic_player.tags).location.x, utils.first(logic_player.tags).location.y,
                     font=("Helvetica", 23), ctag='Player')
        self.logic_player = logic_player
        self.tags_component = [
            TextComponent(tag.tag_id, '.', Player.colors[index], 0, 0, ctag='Tag',
                          font=("Helvetica", 30))
            for index, tag in enumerate(utils.as_list(logic_player.tags))
        ]
        self.info = TextComponent(str(cid) + "_info", "", "white", 0, 0, font=("Helvetica", 6))

    def draw(self):
        super(Player, self).draw()
        [t.draw() for t in self.tags_component]
        self.info.draw()

    def get_tag_component(self, tag: Tag):
        for ctag in self.tags_component:
            if tag.tag_id == ctag.cid:
                return ctag
        return None

    def set_tag_location(self, tag: Tag, use_projected_location=True):
        tag_component = self.get_tag_component(tag)
        if tag_component is not None:
            if use_projected_location:
                tag_component.set_projected_location(tag.location.x, tag.location.y)
            else:
                tag_component.set_location(tag.location.x, tag.location.y)
            self.update_location()
            self.update_player_info()
            return True
        return False

    def update_location(self):
        tags_x = [c.x for c in self.tags_component]
        tags_y = [c.y for c in self.tags_component]
        loc_x = math.fsum(tags_x) / len(tags_x)
        loc_y = math.fsum(tags_y) / len(tags_y)
        self.set_location(loc_x, loc_y)

    def update_player_info(self):
        if Settings.STATS_FOR_NERDS:
            text = str(round(self.logic_player.speed(), Settings.ROUND_NUMBER)) + "\n" + \
                   str(round(self.logic_player.direction(), Settings.ROUND_NUMBER)) + "\n" + \
                   str(round(self.logic_player.acceleration(), Settings.ROUND_NUMBER))
            location = self.loc()
            self.info.change_text(text)
            self.info.set_location(location[0] + 20, location[1])


class Ball(TextComponent):
    def __init__(self, cid, x, y):
        super(Ball, self).__init__(cid, ".", "black", x, y, font=("Helvetica", 32), ctag="ball")
        self.info = TextComponent("ball_info", "", "white", 0, 0, font=("Helvetica", 6))
        self.circle = None

    def draw(self):
        super(Ball, self).draw()
        self.info.draw()

    def update_info(self, tag: Tag, ball: Ball):
        if Settings.STATS_FOR_NERDS:
            text = str(round(tag.speed, Settings.ROUND_NUMBER)) + "\n" + \
                   str(round(tag.direction, Settings.ROUND_NUMBER)) + "\n" + \
                   str(round(ball.angle_arafeh, Settings.ROUND_NUMBER)) + "\n" + \
                   str(round(tag.acceleration, Settings.ROUND_NUMBER))
            location = self.loc()
            self.info.change_text(text)
            self.info.set_location(location[0] + 20, location[1] - 10)

    # def update_circle(self, r):
    #     if self.circle is None:
    #         self.circle = Util.create_circle(self.loc()[0], self.loc()[1], r, self.ctx)
    #     else:
    #         self.ctx.delete(self.circle)
    #         self.circle = None
    #         self.update_circle(r)


class Application:
    _app = None

    @staticmethod
    def instance():
        if Application._app is None:
            Application._app = Application()
        return Application._app

    def __init__(self):
        self.root = tkinter.Tk()
        self.ctx = tkinter.Canvas(self.root, bg="white", height=Protocol.FIELD.HEIGHT + Protocol.FIELD.Y_START * 2,
                                  width=Protocol.FIELD.WIDTH + Protocol.FIELD.X_START * 2)
        self.players: List[Player] = []
        self.ball: Ball = None

    def draw_pitch(self, image):
        self.ctx.create_image(0, 0, anchor=tkinter.NW, image=image)

    @staticmethod
    def rescale_map():
        Protocol.FIELD.WIDTH *= Settings.SCALE_MAP
        Protocol.FIELD.HEIGHT *= Settings.SCALE_MAP
        Protocol.FIELD.X_START *= Settings.SCALE_MAP
        Protocol.FIELD.Y_START *= Settings.SCALE_MAP
        Protocol.FIELD.SCALE_Y *= Settings.SCALE_MAP
        Protocol.FIELD.SCALE_X *= Settings.SCALE_MAP

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

    def place_tag(self, tag: Tag, use_projected_location=True):
        for player in self.players:
            if player.set_tag_location(tag, use_projected_location):
                return True
        return False

    def loop(self):
        self.ctx.pack()
        self.root.mainloop()
