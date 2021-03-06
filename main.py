import threading
import tkinter
from datetime import datetime
from time import sleep

from PIL import ImageTk, Image
import gui
import stdout
import time_series
from Coordinates import Coordinates
from Player import Player
from Protocol import Protocol
from Team import Team
from aio import *
from Ball import Ball
from logic import Tag
from pipes import PlayerFileSaverPipe

OFFSIDE = None
CAN_MOVE = True

gui.Application.rescale_map()
# initialize teams
t2 = Team('Team Blue', 'blue', Protocol.SIDE_TOP)
t1 = Team('Team Red', 'red', Protocol.SIDE_BOT)

# initialize players team 1
for i in range(Settings.NUMBER_OF_PLAYERS_PER_TEAM):
    player = Player(i, t1)
    for tag in Settings.PLAYERS_TAGS[i]:
        player.init_tag(Tag(tag))

# initialize players team 2
for i in range(Settings.NUMBER_OF_PLAYERS_PER_TEAM, Settings.NUMBER_OF_PLAYERS_PER_TEAM * 2):
    player = Player(i, t2)
    for tag in Settings.PLAYERS_TAGS[i]:
        player.init_tag(Tag(tag, Coordinates(Protocol.FIELD.REAL_WIDTH / 2, Protocol.FIELD.REAL_HEIGHT, 0)))

# initialize ball
players = t1.players + t2.players
ball = Ball(Coordinates(0, 0, 0), players)

# initialize UI
app = gui.Application.instance()

app.draw_pitch()

for player in players:
    gui_player = gui.Player(player.player_id, player)
    player.set_player_gui(gui_player)
    app.add_player(gui_player)

app.set_ball(gui.Ball(Settings.BALL_TAG, ball.location.x, ball.location.y))
app.place_all()


def detect_mis_located_players():
    if t1.possessing_ball():
        t1.set_offside_attribute(t2)
    if t2.possessing_ball():
        t2.set_offside_attribute(t1)


def reset():
    global CAN_MOVE
    for _pl in t1.players + t2.players:
        _pl.reset()
    ball.player_possessing.is_possessing_ball = True
    app.ctx.delete(OFFSIDE)
    CAN_MOVE = True


# for _player in players:
#     print('player', _player.player_id, 'placed',
#           [_player.get_player_locations()[0].x, _player.get_player_locations()[0].y])

detect_mis_located_players()

index = 0


def stream_handler(data):
    global index
    index += 1
    missing = [HighShakeFilteredInfo.HF_SPEED, HighShakeFilteredInfo.HF_DIRECTION,
               HighShakeFilteredInfo.HF_ACCELERATION, HighShakeFilteredInfo.HF_DISTANCE]
    for item in missing:
        if item not in data:
            data[item] = 0.0
    # print(index)
    received_tag = Tag(data[TagStreamParser.TAG], data[TagStreamParser.TIMESTAMP],
                       Coordinates(data[TagStreamParser.X], data[TagStreamParser.Y] + (Protocol.FIELD.REAL_HEIGHT / 2),
                                   data[TagStreamParser.Z]), data[SpeedDirectionPipe.SPEED],
                       data[SpeedDirectionPipe.DIRECTION], data[SpeedDirectionPipe.ACCELERATION],
                       data[SpeedDirectionPipe.DISTANCE], data[HighShakeFilteredInfo.HF_SPEED],
                       data[HighShakeFilteredInfo.HF_DIRECTION], data[HighShakeFilteredInfo.HF_ACCELERATION],
                       data[HighShakeFilteredInfo.HF_DISTANCE])
    global OFFSIDE
    global CAN_MOVE
    stdout.out(received_tag)

    if received_tag.tag_id == Settings.BALL_TAG: #or received_tag.tag_id == Settings.BALL_TAG2:
        app.ball.set_projected_location(received_tag.location.x, received_tag.location.y)
        detect_mis_located_players()
        is_offside, offside_type = ball.update_ball(received_tag)
        app.ball.update_info(received_tag, ball)
        if is_offside and CAN_MOVE:
            utils.to_file(players, ball, True)
            CAN_MOVE = False
            ball.player_possessing.change_display()
            text = ""
            if offside_type == 1:
                text = "OFFSIDE!"
            elif offside_type == 2:
                text = "POTENTIAL OFFSIDE (low filter)!"
            elif offside_type == 3:
                text = "POTENTIAL OFFSIDE (high filter)!"
            OFFSIDE = app.ctx.create_text(Protocol.FIELD.WIDTH / 2, Protocol.FIELD.HEIGHT / 2, fill="black",
                                          font="Times 32 bold", text=text)
            start_time = threading.Timer(4, reset)
            start_time.start()
        else:
            utils.to_file(players, ball, False)

    else:
        for _p in players:
            if _p.set_tag(received_tag):
                _p.change_display()
                break
        app.place_tag(received_tag)

        # dummy 4th player
        # _t1 = Tag(utils.as_list(players[-1].tags)[0].tag_id, 0,
        #           Coordinates(Protocol.FIELD.REAL_WIDTH / 2, Protocol.FIELD.REAL_HEIGHT, 0))
        # _t2 = Tag(utils.as_list(players[-1].tags)[1].tag_id, 0,
        #           Coordinates(Protocol.FIELD.REAL_WIDTH / 2, Protocol.FIELD.REAL_HEIGHT, 0))
        # players[-1].set_tag(_t1)
        # app.place_tag(_t1)
        # players[-1].set_tag(_t2)
        # app.place_tag(_t2)
        # players[-1].change_display()

        detect_mis_located_players()


# # start thread generating data and wait for it to end
# dg = DataGenerator(stream_handler, Settings.IS_READ_FROM_FILE, Settings.FILE_PATH)
# dg.start()

class BallHandlerPipe(Pipe):

    def __init__(self, ball_tags):
        super().__init__()
        self.ball_tags = ball_tags
        self.received_tags = []

    def next(self, data) -> object:
        force_send = False
        if data[TagStreamParser.TAG] in self.ball_tags:

            if data[TagStreamParser.TAG] in [tt[TagStreamParser.TAG] for tt in self.received_tags]:
                force_send = True
                self.source.buffer.append(utils.as_reader_input(data[TagStreamParser.TAG], data[TagStreamParser.X],
                                                                data[TagStreamParser.Y], 0.0))
            else:
                self.received_tags.append(data)

            if self.is_all_received() or force_send:
                cp = {
                    TagStreamParser.TAG: Settings.BALL_TAG,
                    TagStreamParser.X: self.avg_of(TagStreamParser.X),
                    TagStreamParser.Y: self.avg_of(TagStreamParser.Y),
                    TagStreamParser.Z: self.avg_of(TagStreamParser.Z),
                    TagStreamParser.TIMESTAMP: data[TagStreamParser.TIMESTAMP],
                    TagStreamParser.POS: data[TagStreamParser.POS],
                    SpeedDirectionPipe.SPEED: self.avg_of(SpeedDirectionPipe.SPEED),
                    SpeedDirectionPipe.DIRECTION: self.avg_of(SpeedDirectionPipe.DIRECTION),
                    SpeedDirectionPipe.ACCELERATION: self.avg_of(SpeedDirectionPipe.ACCELERATION),
                    SpeedDirectionPipe.DISTANCE: self.avg_of(SpeedDirectionPipe.DISTANCE),
                    HighShakeFilteredInfo.HF_SPEED: self.avg_of(HighShakeFilteredInfo.HF_SPEED),
                    HighShakeFilteredInfo.HF_DIRECTION: self.avg_of(HighShakeFilteredInfo.HF_DIRECTION),
                    HighShakeFilteredInfo.HF_ACCELERATION: self.avg_of(HighShakeFilteredInfo.HF_ACCELERATION),
                    HighShakeFilteredInfo.HF_DISTANCE: self.avg_of(HighShakeFilteredInfo.HF_DISTANCE),
                }
                self.received_tags = []
                return cp
            else:
                return None
        return data

    def is_all_received(self):
        return len(self.received_tags) == len(self.ball_tags)

    def avg_of(self, of):
        avg = 0
        for item in self.received_tags:
            avg += item[of]
        return avg / len(self.received_tags)


file_date = datetime.now().strftime("%b-%d-%Y_%H-%M-%S")
stream_source = FileStreamSource(Settings.FILE_PATH) if Settings.IS_READ_FROM_FILE else ComStreamSource(
    Settings.COM_PORT_TAG_READER, Settings.COM_SETTINGS)
streamers = Streamer(stream_source)
if Settings.IS_READ_FROM_FILE:
    streamers.add_pipe(FrequencyControlPipe(Settings.READING_FREQUENCY))
else:
    streamers.add_pipe(FileSaverPipe("logs/Raw-" + file_date + ".txt"))
streamers.add_pipe(TagStreamParser())
streamers.add_pipe(HighShakeFilteredInfo(Settings.HIGH_SHAKE_FILTER_MARGIN))
streamers.add_pipe(ShakeFilter(Settings.SHAKE_FILTER_MARGIN))
# streamers.add_pipe(MovementFilterPipe())
streamers.add_pipe(SpeedDirectionPipe())
# streamers.add_pipe(time_series.AutoCorrectionPipe())
# streamers.add_pipe(FileSaverPipe("logs/Parsed-" + file_date + ".txt", map=utils.csv))
streamers.add_pipe(PlayerFileSaverPipe("plogs/" + file_date))
streamers.add_pipe(BallHandlerPipe([Settings.BALL_TAG, Settings.BALL_TAG2]))
streamers.add_pipe(HandlerPipe(stream_handler))
streamers.add_pipe(stdout.ConsoleUpdatePipe())
streamers.add_pipe(stdout.StdPipe())

streamers.start()


def on_closing():
    # dg.file.close()
    streamers.stop()
    app.root.destroy()


app.root.protocol("WM_DELETE_WINDOW", on_closing)
app.loop()
