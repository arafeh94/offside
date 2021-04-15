from typing import List

from rich.console import Console
from rich.table import Table

import Settings
from Ball import Ball
from Player import Player

console = Console()


def update_table(players: List[Player], ball: Ball):
    pass
    # console.clear()
    # table = Table(show_header=True, header_style='bold #2070b2',
    #               title='[bold]ACTIVE [#2070b2]PLAYER[/#2070b2] MONITOR')
    # table.add_column('Player', justify='right')
    # table.add_column('Tag', justify='right')
    # table.add_column('Speed', justify='right')
    # table.add_column('Direction', justify='right')
    # table.add_column('Acceleration', justify='right')
    # for player in players:
    #     for key_tag in player.tags:
    #         tag = player.tags[key_tag]
    #         table.add_row(str(player.player_id), key_tag, str(tag.speed), str(tag.direction), str(tag.acceleration))
    # console.print(table)
