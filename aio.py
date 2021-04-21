import math
import multiprocessing
import threading
import time
from abc import abstractmethod
from datetime import datetime

import Settings
import utils
import serial


class StreamSource:
    @abstractmethod
    def read_line(self):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass


class ArrayStreamSource(StreamSource):
    def __init__(self, array: []):
        self.array = iter(array)

    def read_line(self):
        try:
            return next(self.array)
        except StopIteration:
            return None

    def open(self):
        pass

    def close(self):
        pass


class FileStreamSource(StreamSource):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.reader = None
        self.row = 0

    def read_line(self):
        # print(self.row)
        self.row += 1
        return self.reader.readline()

    def open(self):
        self.reader = open(self.file_path, "r")

    def close(self):
        self.reader.close()


class ComStreamSource(StreamSource):
    def __init__(self, port: str, baudrate: int):
        self.reader = serial.Serial(port, baudrate)

    def read_line(self):
        return self.reader.readline()

    def open(self):
        pass
        # self.reader.open()

    def close(self):
        pass
        # self.reader.close()


class Pipe:
    def __init__(self):
        self.source = None

    @abstractmethod
    def next(self, data) -> object:
        pass

    def on_close(self):
        pass


class Streamer:
    STATUS_STOPPED = '1'
    STATUS_RUNNING = '0'
    STATUS_CLOSED = '2'

    def __init__(self, source: StreamSource):
        self.source = source
        self.pipes = []
        self.status = Streamer.STATUS_STOPPED
        self.thread = None
        self.buffer = []

    def add_pipe(self, pipe: Pipe):
        pipe.source = self
        self.pipes.append(pipe)

    def next_reading(self):
        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        return self.source.read_line()

    def run(self):
        self.status = Streamer.STATUS_RUNNING
        self.source.open()
        while self.status == Streamer.STATUS_RUNNING:
            reading = self.next_reading()
            if reading is not None:
                local_pipe = iter(self.pipes)
                try:
                    next_pipe = next(local_pipe)
                    pipe_result = next_pipe.next(reading)
                    while pipe_result is not None:
                        next_pipe = next(local_pipe)
                        pipe_result = next_pipe.next(pipe_result)
                except StopIteration:
                    pass
            else:
                self.status = Streamer.STATUS_STOPPED
                break

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.status = Streamer.STATUS_STOPPED
        for pipe in self.pipes:
            pipe.on_close()
        self.source.close()


class ConsoleOutPipe(Pipe):
    def next(self, data) -> object:
        print(data)
        return data


class FrequencyControlPipe(Pipe):
    def __init__(self, frequency=10.):
        super().__init__()
        self.frequency = frequency

    def next(self, data) -> object:
        if self.frequency > 0:
            time.sleep(1 / self.frequency)
        return data


# noinspection PyBroadException
class TagStreamParser(Pipe):
    POS = 'pos'
    TIMESTAMP = 'timestamp'
    TAG = 'tag'
    X = 'x'
    Y = 'y'
    Z = 'z'

    def next(self, data) -> object:
        try:
            line = str(data).split(",")
            if len(line) < 5:
                return None
            timestamp = time.time()
            pos = str(line[1])
            tag = str(line[2])
            x = float(line[3])
            y = float(line[4])
            z = float(line[5])
            if math.isnan(x) or math.isnan(y) or math.isnan(z):
                return None
            return {'pos': pos, 'timestamp': timestamp, 'tag': tag, 'x': x, 'y': y, 'z': z}
        except Exception as e:
            return None

class MovementFilterPipe(Pipe):
    RESET_TICK_COUNTER = 10

    def __init__(self):
        super().__init__()
        self.dict = {}
        self.tag_counter = {}

    def get(self, tag_id):
        if tag_id not in self.dict:
            self.dict[tag_id] = None
        return self.dict[tag_id]

    def get_tag_counter(self, tag_id):
        if tag_id not in self.tag_counter:
            self.tag_counter[tag_id] = self.RESET_TICK_COUNTER
        return self.tag_counter[tag_id]

    def tick(self, tag_id):
        counter = self.get_tag_counter(tag_id)
        if counter == 0:
            return True
        else:
            self.tag_counter[tag_id] = counter - 1
            return False

    def reset_tag_counter(self, tag_id):
        self.tag_counter[tag_id] = self.RESET_TICK_COUNTER

    def set(self, tag_id, data):
        self.dict[tag_id] = data

    def next(self, data) -> object:
        new = data
        old = self.get(tag_id=data[TagStreamParser.TAG])
        tag_id = data[TagStreamParser.TAG]
        if old is not None and new[TagStreamParser.X] == old[TagStreamParser.X] and \
                new[TagStreamParser.Y] == old[TagStreamParser.Y] and \
                new[TagStreamParser.Z] == old[TagStreamParser.Z]:
            if not self.tick(tag_id):
                return None
        self.reset_tag_counter(tag_id)
        self.set(data[TagStreamParser.TAG], new)
        return data


class ShakeFilter(Pipe):
    def __init__(self, margin=0.035):
        super().__init__()
        self.dict = {}
        self.margin = margin

    def get(self, tag_id):
        if tag_id not in self.dict:
            self.dict[tag_id] = None
        return self.dict[tag_id]

    def set(self, tag_id, data):
        self.dict[tag_id] = data

    def next(self, new_data) -> object:
        tag_id = new_data[TagStreamParser.TAG]
        old_data = self.get(tag_id)
        if old_data is None:
            self.set(tag_id, new_data)
            return new_data
        else:
            old_point = [old_data[TagStreamParser.X], old_data[TagStreamParser.Y], old_data[TagStreamParser.Z]]
            new_point = [new_data[TagStreamParser.X], new_data[TagStreamParser.Y], new_data[TagStreamParser.Z]]
            is_shaking = self.is_shaking(old_point, new_point)
            return_data = new_data
            if is_shaking:
                return_data[TagStreamParser.X] = old_data[TagStreamParser.X]
                return_data[TagStreamParser.Y] = old_data[TagStreamParser.Y]
                return_data[TagStreamParser.Z] = old_data[TagStreamParser.Z]

            result = return_data
            self.set(tag_id, result)
            return result

    def is_shaking(self, old_data, new_data):
        distance = utils.dist(old_data, new_data)
        return distance < self.margin


class SpeedDirectionPipe(Pipe):
    SPEED = 'speed'
    DIRECTION = 'direction'
    ACCELERATION = 'acceleration'
    DISTANCE = 'distance'

    def __init__(self):
        super().__init__()
        self.dict = {}

    def get(self, tag_id):
        if tag_id not in self.dict:
            self.dict[tag_id] = None
        return self.dict[tag_id]

    def set(self, tag_id, data):
        self.dict[tag_id] = data

    def next(self, data) -> object:
        tag_id = data[TagStreamParser.TAG]
        history = self.get(tag_id)
        if history is None:
            return_result = data
            return_result[SpeedDirectionPipe.SPEED] = 0
            return_result[SpeedDirectionPipe.DIRECTION] = 0
            return_result[SpeedDirectionPipe.DISTANCE] = 0
            return_result[SpeedDirectionPipe.ACCELERATION] = 0
            self.set(tag_id, return_result)
            return return_result
        else:
            new_data = data
            old_data = self.get(tag_id)
            distance = self.distance(old_data, new_data)
            speed = self.speed(old_data, new_data)
            direction = self.direction(old_data, new_data)
            acc = self.acceleration(old_data, new_data, speed)
            return_result = new_data
            return_result[SpeedDirectionPipe.SPEED] = speed
            return_result[SpeedDirectionPipe.DIRECTION] = direction
            return_result[SpeedDirectionPipe.DISTANCE] = distance
            return_result[SpeedDirectionPipe.ACCELERATION] = acc
            self.set(tag_id, return_result)
            return return_result

    # noinspection PyMethodMayBeStatic
    # need to optimize
    def distance(self, old, new):
        old_point = [old[TagStreamParser.X], old[TagStreamParser.Y], old[TagStreamParser.Z]]
        new_point = [new[TagStreamParser.X], new[TagStreamParser.Y], new[TagStreamParser.Z]]
        distance = utils.dist(old_point, new_point)
        return distance

    # noinspection PyMethodMayBeStatic
    def speed(self, old, new):
        old_time = old[TagStreamParser.TIMESTAMP]
        new_time = new[TagStreamParser.TIMESTAMP]
        old_point = [old[TagStreamParser.X], old[TagStreamParser.Y], old[TagStreamParser.Z]]
        new_point = [new[TagStreamParser.X], new[TagStreamParser.Y], new[TagStreamParser.Z]]
        distance = utils.dist(old_point, new_point)
        dif_time = new_time - old_time
        if dif_time > 0:
            speed = distance / dif_time
        else:
            speed = 0
        return speed

    # noinspection PyMethodMayBeStatic
    def direction(self, old, new):
        x = new[TagStreamParser.X] - old[TagStreamParser.X]
        y = new[TagStreamParser.Y] - old[TagStreamParser.Y]
        # x = new[TagStreamParser.X]
        # y = new[TagStreamParser.Y]
        direction = math.atan2(y, x)
        return math.degrees(direction)

    # noinspection PyMethodMayBeStatic
    def acceleration(self, old, new, new_speed):
        old_time = old[TagStreamParser.TIMESTAMP]
        new_time = new[TagStreamParser.TIMESTAMP]
        old_speed = old[SpeedDirectionPipe.SPEED]
        dif_time = new_time - old_time
        try:
            acceleration = (new_speed - old_speed) / dif_time
            return acceleration
        except ZeroDivisionError:
            return 0


# noinspection PyUnresolvedReferences,PyTypeChecker
class HighShakeFilteredInfo(Pipe):
    HF_SPEED = "hf_speed"
    HF_DIRECTION = "hf_direction"
    HF_ACCELERATION = "hf_accelerometer"
    HF_DISTANCE = "hf_distance"

    def __init__(self, high_margin):
        super().__init__()
        self.shake_filter = ShakeFilter(high_margin)
        self.info_appender = SpeedDirectionPipe()

    def next(self, data) -> object:
        copy = data.copy()
        copy = self.shake_filter.next(copy)
        copy = self.info_appender.next(copy)
        data[self.HF_SPEED] = copy[SpeedDirectionPipe.SPEED]
        data[self.HF_DIRECTION] = copy[SpeedDirectionPipe.DIRECTION]
        data[self.HF_ACCELERATION] = copy[SpeedDirectionPipe.ACCELERATION]
        data[self.HF_DISTANCE] = copy[SpeedDirectionPipe.DISTANCE]
        return data


class FileSaverPipe(Pipe):

    def __init__(self, output_path, map=None):
        super().__init__()
        self.output_path = output_path
        self.writer = open(output_path, "w")
        self.map = map

    def next(self, data) -> object:
        self.write(data)
        return data

    def write(self, params):
        if self.map is not None:
            params = self.map(params)
        writings = str(params) + '\n'
        self.writer.write(writings)

    def on_close(self):
        self.writer.flush()
        self.writer.close()


class HandlerPipe(Pipe):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler

    def next(self, data) -> object:
        if self.handler is not None:
            self.handler(data)
        return data


class StdBuffer:
    def __init__(self, max_buffer):
        self.buffer = {}
        self.volatile_buffer = []
        self.max_buffer = max_buffer

    def register(self, printable, tag=None):
        if tag is None:
            while len(self.volatile_buffer) > self.max_buffer:
                self.volatile_buffer.pop(0)
            self.volatile_buffer.append(printable)
        else:
            self.buffer[tag] = printable

    def get_buffer(self):
        return list(self.buffer.values()) + self.volatile_buffer
