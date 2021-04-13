import math
import sched, time
import threading
import tkinter
from datetime import datetime
from random import randint

from Coordinates import Coordinates
from Protocol import Protocol


class StreamData:
    def __init__(self, timestamp, tag_id, x, y, z, speed, direction):
        self.tag_id = tag_id
        self.location = Coordinates(x, y, z)
        self.speed = speed
        self.direction = direction
        self.timestamp = timestamp

    def __str__(self):
        return "tag: % s, " \
               "loca: % s:% s" % (self.tag_id, self.location.x, self.location.y)


class DataGenerator:
    def __init__(self, handler, is_read_from_file=False, file_path=None):
        self.handler = handler
        self.d = None
        self.is_read_from_file = is_read_from_file
        if is_read_from_file:
            self.file = open(file_path, "r")
        else:
            x = datetime.now().strftime("%b-%d-%Y_%H-%M-%S")
            self.file = open("logs/" + x + ".txt", "x")

    def start(self):
        self.d = threading.Thread(name='daemon', target=self.run, args=[])
        self.d.setDaemon(True)
        self.d.start()

    def on_closing(self):
        self.file.close()

    def run(self):
        if not self.is_read_from_file:
            import serial
            ser = serial.Serial(Protocol.COM_PORT_TAG_READER, Protocol.COM_SETTINGS)
        else:
            ser = self.file
        while True:
            read_line = ser.readline()

            if not self.is_read_from_file:
                self.file.write(str(read_line) + "\n")
            line = str(read_line).split(",")
            if len(line) < 5:
                continue
            tag = int(line[2])
            x = float(line[3])
            y = float(line[4]) + Protocol.FIELD.REAL_HEIGHT / 2
            # if tag == 4830:
            #     y = float(line[4])
            # if tag == 337:
            #     y = Protocol.FIELD.REAL_HEIGHT
            #     x = Protocol.FIELD.REAL_WIDTH/2

            z = float(line[5])
            if not math.isnan(x) and not math.isnan(y) and not math.isnan(z):
                location = Coordinates(x, y, z)
                data = StreamData(tag, location, 0)
                self.handler(data)
                time.sleep(0.005)
