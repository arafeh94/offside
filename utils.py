import Settings


def dist(point1, point2):
    return (((point1[0] - point2[0]) ** 2) +
            ((point1[1] - point2[1]) ** 2) +
            ((point1[2] - point2[2]) ** 2)) ** 0.5


def tuple_to_csv(_tuple):
    string = ""
    for item in _tuple:
        string += str(item) + ","
    return string.rstrip(",")


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
