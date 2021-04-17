import math

from statsmodels.tsa.ar_model import AutoReg

import stdout
import utils
from aio import TagStreamParser, Pipe, SpeedDirectionPipe


def predict_ar(d1data):
    model = AutoReg(d1data, lags=1, old_names=False)
    model_fit = model.fit()
    return model_fit.predict(len(d1data), len(d1data))[0]


class AutoCorrectionPipe(Pipe):
    def __init__(self):
        super().__init__()
        self.tags_status = {}
        self.tags_history = {}

    def is_received(self, tag_id):
        if tag_id not in self.tags_status:
            self.tags_status[tag_id] = False
        return self.tags_status[tag_id]

    def _init_tag(self, tag):
        if tag not in self.tags_history:
            self.tags_history[tag] = {}
        if 'x' not in self.tags_history[tag]:
            self.tags_history[tag]['x'] = []
        if 'y' not in self.tags_history[tag]:
            self.tags_history[tag]['y'] = []
        if 'speed' not in self.tags_history[tag]:
            self.tags_history[tag]['speed'] = []
        if len(self.tags_history[tag]['x']) > 20:
            self.tags_history[tag]['x'].pop(0)
        if len(self.tags_history[tag]['y']) > 20:
            self.tags_history[tag]['y'].pop(0)
        if len(self.tags_history[tag]['speed']) > 20:
            self.tags_history[tag]['speed'].pop(0)

    def append(self, tag, x, y, speed):
        self._init_tag(tag)
        self.tags_history[tag]['x'].append(x)
        self.tags_history[tag]['y'].append(y)
        self.tags_history[tag]['speed'].append(speed)

    def get_tag_history(self, tag, var):
        self._init_tag(tag)
        return self.tags_history[tag][var]

    def is_all_received(self):
        if len(self.tags_status.values()) < utils.tag_numbers():
            return False
        for tag in self.tags_status.values():
            if not tag:
                return False
        return True

    def reset(self):
        for tag in self.tags_status:
            self.tags_status[tag] = False

    def next(self, data) -> object:
        pos = data[TagStreamParser.POS]
        tag = data[TagStreamParser.TAG]
        x = data[TagStreamParser.X]
        y = data[TagStreamParser.Y]
        z = data[TagStreamParser.Z]
        speed = data[SpeedDirectionPipe.SPEED]
        if pos == "-1":
            speed_history = self.get_tag_history(tag, 'speed')
            self.append(tag, x, y, speed_history[-1])
            return data
        self.append(tag, x, y, speed)

        if self.is_received(tag):
            for key_tag in self.tags_status:
                is_received = self.tags_status[key_tag]
                if not is_received:
                    try:
                        # speed_history = self.get_tag_history(key_tag, 'speed')
                        # speed_next = predict_ar(speed_history)
                        # diff1 = 1
                        # if speed_history[-2] != 0:
                        #     diff1 = speed_history[-1] / speed_history[-2]
                        # else:
                        #     diff1 = speed_next / speed_history[-1]
                        #
                        # if key_tag == "1833":
                        # diff2 = speed_next / speed_history[-1]
                        x_history = self.get_tag_history(key_tag, 'x')
                        x_next = (x_history[-1] - x_history[-2]) / 1.08 + x_history[-1]
                        y_history = self.get_tag_history(key_tag, 'y')
                        y_next = (y_history[-1] - y_history[-2]) / 1.08 + y_history[-1]
                        x_next = predict_ar(x_history)
                        y_next = predict_ar(y_history)
                        stdout.out(key_tag + ':predicted:(' + str(x) + ', ' + str(y) + ')', 'predicted')
                        self.source.buffer.append(utils.as_reader_input(key_tag, x_next, y_next, 0.0))
                        self.tags_status[key_tag] = True
                    except:
                        print("samira")
        if self.is_all_received():
            self.reset()
        self.tags_status[tag] = True
        return data
