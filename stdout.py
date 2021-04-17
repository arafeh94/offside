from typing import List

from rich.console import Console
from rich.table import Table

import Settings
import utils
from Ball import Ball
from Player import Player
from aio import Pipe, TagStreamParser, SpeedDirectionPipe, StdBuffer

console = Console()
std = StdBuffer(10)


def display_buffer():
    console.clear(True)
    for printable in std.get_buffer():
        console.print(printable)


def out(printable, tag=None):
    std.register(printable, tag)


class ConsoleUpdatePipe(Pipe):
    def __init__(self):
        super().__init__()
        self.players = {}

    def next(self, data) -> object:
        tag_id = data[TagStreamParser.TAG]
        player_id = utils.tag_to_player_id(tag_id)
        speed = round(data[SpeedDirectionPipe.SPEED], Settings.ROUND_NUMBER)
        direction = round(data[SpeedDirectionPipe.DIRECTION], 0)
        acceleration = round(data[SpeedDirectionPipe.ACCELERATION], Settings.ROUND_NUMBER)
        if player_id not in self.players:
            self.players[player_id] = {}
        if tag_id not in self.players[player_id]:
            self.players[player_id][tag_id] = {}
        self.players[player_id][tag_id] = {
            "speed": speed,
            "direction": direction,
            "acceleration": acceleration
        }
        self.update_table()
        return data

    def update_table(self):
        table = Table(show_header=True, header_style='bold #2070b2',
                      title='[bold]ACTIVE [#2070b2]PLAYER[/#2070b2] MONITOR')
        table.add_column('Player', justify='right')
        table.add_column('Tag', justify='right')
        table.add_column('Speed', justify='right')
        table.add_column('Direction', justify='right')
        table.add_column('Acceleration', justify='right')
        for player_id_key in self.players:
            player_tags = self.players[player_id_key]
            for tag_key in player_tags:
                tag_info = player_tags[tag_key]
                table.add_row(str(player_id_key), tag_key, str(tag_info['speed']), str(tag_info['direction']),
                              str(tag_info['acceleration']))
        out(table, "info_table")


class StdPipe(Pipe):
    def __init__(self, update_freq=1):
        super().__init__()
        self.sec = 1 / update_freq
        self.update = True

    def next(self, data) -> object:
        if not self.update:
            return data

        if self.update:
            if self.update:
                display_buffer()
                self.toggle()
            utils.run_after(self.sec, self.toggle)
            return data

    def toggle(self):
        self.update = not self.update
