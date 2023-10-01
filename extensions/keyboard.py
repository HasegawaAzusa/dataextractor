from . import success_echo, fail_echo, debug_echo
from .utils import unhexlify, hexlify
from .tsharkutils import get_layers
import click
import json
from collections import defaultdict

CAPTURE_FILTER_PARAMS = ('usbhid.data', 'usb.capdata', )
"""
Parameters that need to be captured
"""

SPECIAL_KEY = dict(
    RET_KEY='<RET>',
    ESC_KEY='<ESC>',
    DEL_KEY='<DEL>',
    TAB_KEY='<TAB>',
    SPACE_KEY='<SPACE>',
    NON_KEY='<NON>',
    GA_KEY='<GA>',
    CAP_KEY='<CAP>',
    F1_KEY='<F1>',
    F2_KEY='<F2>',
    F3_KEY='<F3>',
    F4_KEY='<F4>',
    F5_KEY='<F5>',
    F6_KEY='<F6>',
    F7_KEY='<F7>',
    F8_KEY='<F8>',
    F9_KEY='<F9>',
    F10_KEY='<F10>',
    F11_KEY='<F11>',
    F12_KEY='<F12>',
    UNKOWN_KEY='<UNKNOWN>',
)
"""
A special key-value dictionary used for debouncing.
"""

NORMAL_KEYS_MAPPING = {
    0: '', 4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h',
    12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p',
    20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x',
    28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6',
    36: '7', 37: '8', 38: '9', 39: '0',
    40: SPECIAL_KEY['RET_KEY'], 41: SPECIAL_KEY['ESC_KEY'], 42: SPECIAL_KEY['DEL_KEY'],
    43: SPECIAL_KEY['TAB_KEY'], 44: SPECIAL_KEY['SPACE_KEY'], 45: '-', 46: '=',
    47: '[', 48: ']', 49: '\\', 50: SPECIAL_KEY['NON_KEY'], 51: ';',
    52: "'", 53: SPECIAL_KEY['GA_KEY'], 54: ',', 55: '.', 56: '/',
    57: SPECIAL_KEY['CAP_KEY'], 58: SPECIAL_KEY['F1_KEY'], 59: SPECIAL_KEY['F2_KEY'],
    60: SPECIAL_KEY['F3_KEY'], 61: SPECIAL_KEY['F4_KEY'], 62: SPECIAL_KEY['F5_KEY'],
    63: SPECIAL_KEY['F6_KEY'], 64: SPECIAL_KEY['F7_KEY'], 65: SPECIAL_KEY['F8_KEY'],
    66: SPECIAL_KEY['F9_KEY'], 67: SPECIAL_KEY['F10_KEY'], 68: SPECIAL_KEY['F11_KEY'],
    69: SPECIAL_KEY['F12_KEY']
}
"""
A mapping table for normal keys.
"""

SHIFT_KEYS_MAPPING = {
    0: '', 4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H',
    12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P',
    20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X',
    28: 'Y', 29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^',
    36: '&', 37: '*', 38: '(', 39: ')',
    40: SPECIAL_KEY['RET_KEY'], 41: SPECIAL_KEY['ESC_KEY'], 42: SPECIAL_KEY['DEL_KEY'],
    43: SPECIAL_KEY['TAB_KEY'], 44: SPECIAL_KEY['SPACE_KEY'], 45: '_', 46: '+',
    47: '{', 48: '}', 49: '|', 50: SPECIAL_KEY['NON_KEY'], 51: '"',
    52: ':', 53: SPECIAL_KEY['GA_KEY'], 54: '<', 55: '>', 56: '?',
    57: SPECIAL_KEY['CAP_KEY'], 58: SPECIAL_KEY['F1_KEY'], 59: SPECIAL_KEY['F2_KEY'],
    60: SPECIAL_KEY['F3_KEY'], 61: SPECIAL_KEY['F4_KEY'], 62: SPECIAL_KEY['F5_KEY'],
    63: SPECIAL_KEY['F6_KEY'], 64: SPECIAL_KEY['F7_KEY'], 65: SPECIAL_KEY['F8_KEY'],
    66: SPECIAL_KEY['F9_KEY'], 67: SPECIAL_KEY['F10_KEY'], 68: SPECIAL_KEY['F11_KEY'],
    69: SPECIAL_KEY['F12_KEY']
}
"""
A mapping table for keys with SHIFT.
"""

SPECIAL_KEYS_MAPPING = {
    SPECIAL_KEY['SPACE_KEY']: ' ', SPECIAL_KEY['RET_KEY']: '\n',
    SPECIAL_KEY['TAB_KEY']: '\t', SPECIAL_KEY['DEL_KEY']: '\b',
}
"""
A mapping table for special keys.
"""

def keypress_from_hiddata(hiddatas: list[bytes], debug: bool = False):
    """
    Generate key information from hid-data

    Param:
        hiddatas: hid-datas, such as [b'\\x00\\x00\\x30\\x00\\x00\\x00\\x00\\x00']
        debug: Whether to output debugging information, False is default
    
    Return:
        A list containing parsed key information
    """
    # Record the pressed keys and map them to the devices they belong to
    pressed_keys = []
    for hid_data in hiddatas:
        if hid_data == b'\x00' * 8:
            # null data
            continue
        if hid_data[0] == 0:
            # normal pressed
            pressed_keys.append(
                NORMAL_KEYS_MAPPING.get(hid_data[2], SPECIAL_KEY['UNKOWN_KEY']))
        elif hid_data[0] & 0b10 != 0 or hid_data[0] & 0b100000 != 0:
            # left shift or right shift is pressed.
            pressed_keys.append(
                SHIFT_KEYS_MAPPING.get(hid_data[2], SPECIAL_KEY['UNKOWN_KEY']))
        else:
            # unkown hid-data
            fail_echo(f'Unkown hid-data: {hexlify(hid_data)}')
            continue
        ### DEBUG
        if debug:
            debug_echo(f'Parse: {hexlify(hid_data)}')
    return pressed_keys

@click.command()
@click.option('-d', '--debug', is_flag=True, default=False, help='Enable debug information')
@click.pass_context
def parse(ctx: click.Context, debug: bool):
    filepath = ctx.obj['filepath']
    tmppath = ctx.obj['tmppath']
    
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
            pressed_keys = {}
            pressed_contents = {}
            for device_id, hiddatas in hiddata_mapping.items():
                keys = keypress_from_hiddata(hiddatas, debug)
                pressed_keys[device_id] = keys
                capital = False
                content = []
                for key in keys:
                    key: str
                    # Priority should be given to handling special keys.
                    if key == SPECIAL_KEY['CAP_KEY']:
                        capital = not capital
                    elif key in SPECIAL_KEY.values():
                        content.append(SPECIAL_KEYS_MAPPING.get(key, ''))
                    else:
                        content.append(key.upper() if capital else key)
                pressed_contents[device_id] = content

            # Output extracted message
            for device_id in hiddata_mapping.keys():
                success_echo(f'Device ID: {device_id}')
                success_echo(f'Raw: {"".join(pressed_keys[device_id])}')
                success_echo(f'Content: {"".join(pressed_contents[device_id])}')
