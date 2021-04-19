# number of players per team
from Protocol import Protocol

NUMBER_OF_PLAYERS_PER_TEAM = 2

# How close a player from the ball to acquire it
PLAYER_POSSESSION_PROXIMITY = 0.4

t1 = '0337'
t2 = '03B0'
t3 = '03EF'
t4 = '1780'
t5 = '1848'
t6 = '46FE'
t7 = '10DB'
t8 = '0095'
t9 = 'tmp1'


BALL_TAG = t1
PLAYERS_TAGS = [
    [t2, t3],  # tags for player 1 4804 left foot 4830 right foots
    [t4, t5],  # ... 2 1780 lef foot 23E6 right foot
    [t6, t7],  # ... 3 45D3 left foot 47EB right foot
    [t8, t9],  # ... 4 dummy
]

TAG_NUMBERS = 7

COM_PORT_TAG_READER = 'COM8'
COM_SETTINGS = 115200

IS_READ_FROM_FILE = True
FILE_PATH = 'old_logs 2/logs/Raw-Apr-17-2021_11-03-15.txt'
# FILE_PATH = 'logs/test.txt'
READING_FREQUENCY = 0

# SHAKE_FILTER_MARGIN = 0.0
SHAKE_FILTER_MARGIN = 0.05
HIGH_SHAKE_FILTER_MARGIN = 0.5

DEFENDANT_BALL_TOUCH_SENSITIVITY = 10
# 10 = 1 second

# 1 is the default map scaling
SCALE_MAP = 1.8

STATS_FOR_NERDS = True
ROUND_NUMBER = 3

####
DISTANCE_THRESHOLD = 0.5
DIRECTION_CURVE_THRESHOLD = 20
PLAYER_POSSESSION_PROXIMITY_MULTIPLIER = 2