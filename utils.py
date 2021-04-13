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
