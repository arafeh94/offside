# number of players per team
NUMBER_OF_PLAYERS_PER_TEAM = 2

# How close a player from the ball to acquire it
PLAYER_POSSESSION_PROXIMITY = 0.25

BALL_TAG = '0337'
PLAYERS_TAGS = [
    ['4804', '4830'], #tags for player 1 4804 left foot 4830 right foots
    ['1780', '23E6'], # ... 2 1780 lef foot 23E6 right foot
    ['45D3', '47EB'], # ... 3 45D3 left foot 47EB right foot
    ['test', 'test'], # ... 4 dummy
]

COM_PORT_TAG_READER = 'COM3'
COM_SETTINGS = 115200

IS_READ_FROM_FILE = False
FILE_PATH = 'AZZ_MULTIPLE_TAG.txt'

READING_FREQUENCY = 400

SHAKE_FILTER_MARGIN = 0.06
