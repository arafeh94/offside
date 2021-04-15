# number of players per team
from Protocol import Protocol

NUMBER_OF_PLAYERS_PER_TEAM = 2

# How close a player from the ball to acquire it
PLAYER_POSSESSION_PROXIMITY = 0.25

BALL_TAG = '0337'
PLAYERS_TAGS = [
    ['4804', '4830'],  # tags for player 1 4804 left foot 4830 right foots
    ['1780', '23E6'],  # ... 2 1780 lef foot 23E6 right foot
    ['45D3', '47EB'],  # ... 3 45D3 left foot 47EB right foot
    ['tag8', 'tag9'],  # ... 4 dummy
]
# PLAYERS_TAGS = [
#     ['4804'],  # tags for player 1 4804 left foot 4830 right foots
#     ['1780'],  # ... 2 1780 lef foot 23E6 right foot
#     ['45D3'],  # ... 3 45D3 left foot 47EB right foot
#     ['tag8'],  # ... 4 dummy
# ]

COM_PORT_TAG_READER = 'COM3'
COM_SETTINGS = 115200

IS_READ_FROM_FILE = True
FILE_PATH = 'old_logs/Raw-Apr-13-2021_12-32-09.txt'
READING_FREQUENCY = 70

# SHAKE_FILTER_MARGIN = 0.0
SHAKE_FILTER_MARGIN = 0.1

DEFENDANT_BALL_TOUCH_SENSITIVITY = 10
# 10 = 1 second

# 1 is the default map scaling
SCALE_MAP = 2.5

STATS_FOR_NERDS = True
ROUND_NUMBER = 3
