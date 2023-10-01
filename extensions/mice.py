from . import success_echo, fail_echo, debug_echo
from .utils import unhexlify, hexlify
from .tsharkutils import get_layers
import click
import json
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import NamedTuple
from enum import IntEnum
import struct

CAPTURE_FILTER_PARAMS = ('usbhid.data', 'usb.capdata', )
"""
Parameters that need to be captured
"""

class MiceStatus(IntEnum):
    MOVE = 0x00
    LEFT_PRESSED = 0x01
    RIGHT_PRESSED = 0x02

MICE_STATUS_FLAGS = {MiceStatus.MOVE: 'move',
                     MiceStatus.LEFT_PRESSED: 'left',
                     MiceStatus.RIGHT_PRESSED: 'right',
                     }

class MicePosition(NamedTuple):
    x: int
    y: int

class MiceMsg(NamedTuple):
    status: MiceStatus
    position: MicePosition

def micemsg_from_hiddata(hiddatas: list[bytes], debug: bool = False):
    """
    Generate mice message from hid-data

    Param:
        hiddatas: hid-datas, such as [b'\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x00']
        
        debug: Whether to output debugging information, False is default
    
    Return:
        A list containing parsed mice message(MiceMsg)
    """
    position = MicePosition(0, 0)
    micemsg: list[MiceMsg] = [MiceMsg(MiceStatus.MOVE, position)]
    for hid_data in hiddatas:
        if len(hid_data) == 4:
            pressed, offset_x, offset_y = struct.unpack('Bbbx', hid_data)
        elif len(hid_data) == 8:
            pressed, offset_x, offset_y = struct.unpack('Bxbbxxxx', hid_data)
        else:
            fail_echo(f'Unkown hid-data: {hexlify(hid_data)}')
            continue
        try:
            status = MiceStatus(pressed)
        except:
            fail_echo(f'Unkown hid-data: {hexlify(hid_data)}')
            continue
        position = MicePosition(position.x + offset_x, position.y - offset_y)
        micemsg.append(MiceMsg(status, position))
    return micemsg

def handle_micemsgs(micemsgs: list[MiceMsg], position: tuple, colors: tuple[str, str, str], alphas: tuple[float, float, float]):
    """
    Parse MiceMsg output pictures

    Param:
        micemsgs - MiceMsg list

        position - The position to be extracted

        colors - Color of trace, left and right

        alphas - Alpha of trace, left and right

    Return:
        fig, ax
    """
    trace_x = []
    trace_y = []
    last_status = micemsgs[0].status
    fig, ax = plt.subplots()
    for msg in micemsgs:
        if msg.status != last_status:
            # Plot
            if MICE_STATUS_FLAGS[last_status] in position:
                ax.plot(trace_x, trace_y, color=colors[last_status], alpha=alphas[last_status])
            trace_x = []
            trace_y = []
            last_status = msg.status
        trace_x.append(msg.position.x)
        trace_y.append(msg.position.y)
    if MICE_STATUS_FLAGS[last_status] in position:
        ax.plot(trace_x, trace_y, color=colors[last_status], alpha=alphas[last_status])
    return fig, ax

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

    with open(tmppath, 'w') as tmpio:
        for filter_param in CAPTURE_FILTER_PARAMS:
            layers = get_layers(filepath, filter_param, debug)

            ### DEBUG
            if debug:
                tmpio.write(json.dumps(layers) + '\n')
                debug_echo(f'Traffic outputs saved in {tmppath}')

            hiddata_mapping = defaultdict(list)
            for layer_pkt in layers:
                layer_pkt: dict
                # Get usb packet
                device_id: int = layer_pkt['usb']['usb.src']
                # Get usb hid-data
                hid_data: bytes = layer_pkt[filter_param]

                # hid_data convert
                hid_data = unhexlify(hid_data)
                hiddata_mapping[device_id].append(hid_data)

            # Generate output information based on hid-data
            for device_id, hiddatas in hiddata_mapping.items():
                micemsgs = micemsg_from_hiddata(hiddatas, debug)
                fig, ax = handle_micemsgs(micemsgs, position, colors, alphas)
                output_filename = f'{filehash}-{device_id}.png'
                if ax.has_data():
                    fig.savefig(output_filename)
                    success_echo(f'Output saved in ./{output_filename}')
            