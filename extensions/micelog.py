from . import success_echo, fail_echo, debug_echo
from .utils import unhexlify, hexlify
from .tsharkutils import get_layers
from .mice import MiceStatus, MICE_STATUS_FLAGS, MicePosition, MiceMsg, handle_micemsgs
import click
import json
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import NamedTuple
from enum import IntEnum
import struct

class MiceStatusFlags(IntEnum):
    LEFT_PRESSED = 0x01
    RIGHT_PRESSED = 0x02
    MIDDLE_PRESSED = 0x04
    MOVE = 0x08

def micemsg_from_micelog(micelog: bytes, debug: bool = False):
    """
    Generate mice message from hid-data

    Param:
        hiddatas: hid-datas, such as [b'\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x00']
        
        debug: Whether to output debugging information, False is default
    
    Return:
        A list containing parsed mice message(MiceMsg)
    """

    if len(micelog) % 3 == 0:
        data_section = [micelog[i:i+3] for i in range(0, len(micelog), 3)]
    elif len(micelog) % 4 == 0:
        data_section = [micelog[i:i+4] for i in range(0, len(micelog), 4)]
    else:
        fail_echo('Could not parse this mice log')
    position = MicePosition(0, 0)
    micemsg: list[MiceMsg] = [MiceMsg(MiceStatus.MOVE, position)]
    for data in data_section:
        if len(data) == 3:
            pressed, offset_x, offset_y = struct.unpack('Bbb', data)
        elif len(data) == 4:
            pressed, offset_x, offset_y = struct.unpack('Bbbx', data)
        else:
            fail_echo(f'Unkown data: {hexlify(data)}')
            continue
        if pressed & MiceStatusFlags.LEFT_PRESSED:
            status = MiceStatus.LEFT_PRESSED
        elif pressed & MiceStatusFlags.RIGHT_PRESSED:
            status = MiceStatus.RIGHT_PRESSED
        elif pressed & MiceStatusFlags.MOVE:
            status = MiceStatus.MOVE
        else:
            fail_echo(f'Unkown data: {hexlify(data)}')
            continue
        position = MicePosition(position.x + offset_x, position.y + offset_y)
        micemsg.append(MiceMsg(status, position))
    return micemsg

@click.command()
@click.option('-d', '--debug', is_flag=True, default=False, help='Enable debug information')
@click.option('-l', '--left', 'position', flag_value=MICE_STATUS_FLAGS[MiceStatus.LEFT_PRESSED], multiple=True, help='Extract mouse left button data')
@click.option('-r', '--right', 'position', flag_value=MICE_STATUS_FLAGS[MiceStatus.RIGHT_PRESSED], multiple=True, help='Extract mouse right button data')
@click.option('-t', '--trace', 'position', flag_value=MICE_STATUS_FLAGS[MiceStatus.MOVE], multiple=True, help='Extract mouse trace data')
@click.pass_context
def parse(ctx: click.Context, position: tuple[str], debug: bool):
    # Default position
    if not position:
        position = ('left', )
    filepath = ctx.obj['filepath']
    tmppath = ctx.obj['tmppath']
    filehash = ctx.obj['filehash']
    colors = ('c', 'r', 'b')
    alphas = (0.5, 1, 1)

    with open(filepath, 'rb') as f:
        micelog = f.read()
    micemsgs = micemsg_from_micelog(micelog, debug)
    print(micemsgs)
    fig, ax = handle_micemsgs(micemsgs, position, colors, alphas)
    output_filename = f'{filehash}.png'
    if ax.has_data():
        fig.savefig(output_filename)
        success_echo(f'Output saved in ./{output_filename}')