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

    def read_line(self):
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
        #self.reader.open()


    def close(self):
        pass
        #self.reader.close()


class Pipe:
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

    def add_pipe(self, pipe: Pipe):
        self.pipes.append(pipe)

    def run(self):
        self.status = Streamer.STATUS_RUNNING
        self.source.open()
        while self.status == Streamer.STATUS_RUNNING:
            reading = self.source.read_line()
            if reading is not None:
                local_pipe = iter(self.pipes)
                try:
                    pipe_result = next(local_pipe).next(reading)
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
        self.frequency = frequency

    def next(self, data) -> object:
        if self.frequency > 0:
            time.sleep(1 / self.frequency)
        return data


# noinspection PyBroadException
class TagStreamParser(Pipe):
    TIMESTAMP = 0
    TAG = 1
    X = 2
    Y = 3
    Z = 4

    def next(self, data) -> object:
        try:
            line = str(data).split(",")
            if len(line) < 5:
                return None
            timestamp = time.time()
            tag = str(line[2])
            x = float(line[3])
            y = float(line[4])
            z = float(line[5])
            if math.isnan(x) or math.isnan(y) or math.isnan(z):
                return None
            return timestamp, tag, x, y, z
        except:
            return None


class ShakeFilter(Pipe):
    def __init__(self, margin=0.035):
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
            return_data = [x for x in new_data]
            if is_shaking:
                return_data[TagStreamParser.X] = old_data[TagStreamParser.X]
                return_data[TagStreamParser.Y] = old_data[TagStreamParser.Y]
                return_data[TagStreamParser.Z] = old_data[TagStreamParser.Z]

            result = tuple(return_data)
            self.set(tag_id, result)
            return result

    def is_shaking(self, old_data, new_data):
        distance = utils.dist(old_data, new_data)
        return distance < self.margin


class SpeedDirectionPipe(Pipe):
    SPEED = 5
    DIRECTION = 6

    def __init__(self):
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
            data = [x for x in data]
            data.append(0)
            data.append(0)
            return_result = tuple(data)
            self.set(tag_id, return_result)
            return return_result
        else:
            new_data = data
            old_data = self.get(tag_id)
            speed = self.speed(old_data, new_data)
            direction = self.direction(old_data, new_data)
            return_result = [x for x in data]
            return_result.append(speed)
            return_result.append(direction)
            return_results = tuple(return_result)
            self.set(tag_id, return_result)
            return return_results

    # noinspection PyMethodMayBeStatic
    def speed(self, old, new):
        old_time = datetime.fromtimestamp(old[TagStreamParser.TIMESTAMP])
        new_time = datetime.fromtimestamp(new[TagStreamParser.TIMESTAMP])
        old_point = [old[TagStreamParser.X], old[TagStreamParser.Y], old[TagStreamParser.Z]]
        new_point = [new[TagStreamParser.X], new[TagStreamParser.Y], new[TagStreamParser.Z]]
        distance = utils.dist(old_point, new_point)
        dif_time = (new_time - old_time).total_seconds()
        if dif_time > 0:
            speed = distance / dif_time
        else:
            speed = 0
        return speed

    # noinspection PyMethodMayBeStatic
    def direction(self, old, new):
        x = new[TagStreamParser.X] - old[TagStreamParser.X]
        y = new[TagStreamParser.Y] - old[TagStreamParser.Y]
        direction = math.atan2(y, x)
        return direction


class FileSaverPipe(Pipe):

    def __init__(self, output_path, map=None):
        self.output_path = output_path
        self.writer = open(output_path, "w")
        self.map = map

    def next(self, data) -> object:
        # x = threading.Thread(target=self.write, args=(data,))
        # x.start()
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
        self.handler = handler

    def next(self, data) -> object:
        if self.handler is not None:
            self.handler(data)
        return data

# if __name__ == "__main__":
#     file_date = datetime.now().strftime("%b-%d-%Y_%H-%M-%S")
#     stream_source = FileStreamSource(Settings.FILE_PATH) if Settings.IS_READ_FROM_FILE else ComStreamSource(
#         Settings.COM_PORT_TAG_READER, Settings.COM_SETTINGS)
#     streamers = Streamer(stream_source)
#     streamers.add_pipe(ConsoleOutPipe())
#     if Settings.IS_READ_FROM_FILE:
#         streamers.add_pipe(FrequencyControlPipe(Settings.READING_FREQUENCY))
#     else:
#         streamers.add_pipe(FileSaverPipe("logs/Raw-" + file_date + ".txt"))
#     streamers.add_pipe(TagStreamParser())
#     streamers.add_pipe(ShakeFilter(Settings.SHAKE_FILTER_MARGIN))
#     streamers.add_pipe(SpeedDirectionPipe())
#     streamers.add_pipe(FileSaverPipe("logs/Parsed-" + file_date + ".txt", map=utils.tuple_to_csv))
#     streamers.run()
