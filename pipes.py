import os
from datetime import datetime

import Settings
import utils
from aio import Pipe


class PlayerFileSaverPipe(Pipe):
    def __init__(self, folder=""):
        self.file_dict = {}
        self.folder = folder
        if not os.path.exists(folder):
            os.makedirs(folder)

    def get_file(self, tag):
        player_id = utils.tag_to_player_id(tag)
        if player_id not in self.file_dict:
            file_name = self.folder + "/id" + player_id + ".txt"
            self.file_dict[player_id] = open(file_name, 'w')
        return self.file_dict[player_id]

    def next(self, data) -> object:
        copy = utils.tuple_to_csv(data) + "\n"
        self.get_file(data[1]).write(copy)
        return data

    def on_close(self):
        for file in self.file_dict.values():
            file.flush()
            file.close()
