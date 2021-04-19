import threading

import Settings


def dist(point1, point2):
    return (((point1[0] - point2[0]) ** 2) +
            ((point1[1] - point2[1]) ** 2) +
            ((point1[2] - point2[2]) ** 2)) ** 0.5


def csv(val):
    if type(val) in (tuple, list):
        return tuple_2_csv(val)
    if type(val) is dict:
        return dict_2_csv(val)
    return "Inconvertible Format"


def tuple_2_csv(val):
    string = ""
    for item in val:
        string += str(item) + ","
    return string.rstrip(",")


def dict_2_csv(dictionary: dict):
    return tuple_2_csv(dictionary.values())


def eof_remover(string: str):
    return string.rstrip("\n").rstrip("\r")


def first(dictionary):
    return list(dictionary.values())[0]


def as_list(dictionary):
    return list(dictionary.values())


def tag_to_player_id(tag):
    if tag == Settings.BALL_TAG:
        return "00"
    else:
        for index, settings_tag in enumerate(Settings.PLAYERS_TAGS):
            if tag in settings_tag:
                return "0" + str(index + 1)
    return "Nan"


def run_after(time_sec, callable):
    start_time = threading.Timer(time_sec, callable)
    start_time.start()


def as_reader_input(tag, x, y, z):
    return 'POS,-1,' + str(tag) + ',' + str(x) + ',' + str(y) + ',' + str(z) + ',30,x03\r\n'


def tag_numbers():
    return Settings.TAG_NUMBERS


def to_file(players, ball):
    st = "-1, BTAG," + str(ball.location.x) + "," + str(ball.location.y) + "," + str(ball.location.z) + "," + "False\n"
    for player in players:
        for tag_id, tag in player.tags.items():
            st += str(player.player_id) + "," + str(tag_id) + "," + str(tag.location.x) + "," + str(
                tag.location.y) + "," + \
                  str(tag.location.z) + "," + str(player.is_offside_alert) + "\n"
    writer = open("last_offside.txt", "w")
    writer.write(st)
