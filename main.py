import threading
import tkinter
from datetime import datetime
from time import sleep

from PIL import ImageTk, Image
import gui
from Ball import Ball
from Coordinates import Coordinates
from DataGenerator import DataGenerator, StreamData
from Player import Player
from Protocol import Protocol
from Team import Team
from aio import *

OFFSIDE = None
CAN_MOVE = True

# initialize teams
t1 = Team('Team Blue', 'blue', Protocol.SIDE_HOME)
t2 = Team('Team Red', 'red', Protocol.SIDE_AWAY)

# initialize players team 1
for i in range(Settings.NUMBER_OF_PLAYERS_PER_TEAM):
    player = Player(i, t1)
    for tag in Settings.PLAYERS_TAGS[i]:
        player.add_tag(tag, Coordinates(0, 0, 0))

# initialize players team 2
for i in range(Settings.NUMBER_OF_PLAYERS_PER_TEAM, Settings.NUMBER_OF_PLAYERS_PER_TEAM * 2):
    player = Player(i, t2)
    for tag in Settings.PLAYERS_TAGS[i]:
        player.add_tag(tag, Coordinates(0, 0, 0))

# initialize ball
players = t1.players + t2.players
ball = Ball(Coordinates(0, 0, 0), players)

# initialize UI
app = gui.Application.instance()
image = ImageTk.PhotoImage(Image.open(Protocol.FIELD.PITCH_PNG))
app.draw_pitch(image)

for player in players:
    gui_player = gui.Player(player.player_id, player.team.side, player.locations[0].x, player.locations[0].y,
                            player.team.color, player.tags)
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


for _player in players:
    print('player', _player.player_id, 'placed', [_player.locations[0].x, _player.locations[0].y])

detect_mis_located_players()


def stream_handler(data):
    _data = StreamData(data[0], data[1], data[2], data[3] + (Protocol.FIELD.REAL_HEIGHT / 2), data[4], data[5], data[6])
    print(data[0], data[1], data[2], data[3])
    global OFFSIDE
    global CAN_MOVE
    if _data.tag_id == Settings.BALL_TAG:
        app.ball.set_projected_location(_data.location.x, _data.location.y)
        detect_mis_located_players()
        is_offside = ball.move_ball(_data.location)
        if is_offside and CAN_MOVE:
            CAN_MOVE = False
            ball.player_possessing.change_display()
            OFFSIDE = app.ctx.create_text(Protocol.FIELD.WIDTH / 2, Protocol.FIELD.HEIGHT / 2, fill="black",
                                          font="Times 16 bold",
                                          text="OFFSIDE HAS BEEN DETECTED!")
            start_time = threading.Timer(2, reset)
            start_time.start()
    else:
        average_player_location = None
        for _p in players:
            if _p.has_tag(_data.tag_id):
                _p.set_player_location_with_duplicate(_data.tag_id, _data.location)
                average_player_location = _p.get_average_location()
                _p.change_display()
                # break
        for _p in app.players:
            if _p.has_tag(_data.tag_id):
                _p.set_projected_location(average_player_location.x, average_player_location.y)
                print(average_player_location.x, average_player_location.y, average_player_location.z)
                break
        detect_mis_located_players()


# # start thread generating data and wait for it to end
# dg = DataGenerator(stream_handler, Settings.IS_READ_FROM_FILE, Settings.FILE_PATH)
# dg.start()


file_date = datetime.now().strftime("%b-%d-%Y_%H-%M-%S")
stream_source = FileStreamSource(Settings.FILE_PATH) if Settings.IS_READ_FROM_FILE else ComStreamSource(
    Settings.COM_PORT_TAG_READER, Settings.COM_SETTINGS)
streamers = Streamer(stream_source)
# streamers.add_pipe(ConsoleOutPipe())
if Settings.IS_READ_FROM_FILE:
    streamers.add_pipe(FrequencyControlPipe(Settings.READING_FREQUENCY))
else:
    streamers.add_pipe(FileSaverPipe("logs/Raw-" + file_date + ".txt"))
streamers.add_pipe(TagStreamParser())
streamers.add_pipe(ShakeFilter(Settings.SHAKE_FILTER_MARGIN))
streamers.add_pipe(SpeedDirectionPipe())
streamers.add_pipe(FileSaverPipe("logs/Parsed-" + file_date + ".txt", map=utils.tuple_to_csv))
streamers.add_pipe(HandlerPipe(stream_handler))
streamers.start()


def on_closing():
    # dg.file.close()
    streamers.stop()
    app.root.destroy()


app.root.protocol("WM_DELETE_WINDOW", on_closing)
app.loop()
