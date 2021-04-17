class Protocol:
    class FIELD:
        REAL_WIDTH = 12.30
        REAL_HEIGHT = 10.54
        REAL_HEIGHT *= 2
        HALF_FIELD = REAL_HEIGHT / 2

        WIDTH = 347
        HEIGHT = 420
        X_START = 44
        Y_START = 66
        SCALE_X = WIDTH / REAL_WIDTH
        SCALE_Y = HEIGHT / REAL_HEIGHT

        PITCH_PNG = "assets/pitch.png"

    # Teams sides
    SIDE_TOP = 0
    SIDE_BOT = 1
