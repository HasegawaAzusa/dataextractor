from . import call_outer, debug_echo
import json

def get_layers(filepath: str, filter: str = '', debug: bool = False):
    ### DEBUG
    if debug:
        debug_echo(f'Parsed file path: {filepath}')
    
    # Get tshark json
    outputs, _ = call_outer(['tshark', '-r', filepath, '-T', 'json', '-Y', filter])
    # Json loads
    pcap = json.loads(outputs)
    # Get layer packets
    layers = [pkt['_source']['layers'] for pkt in pcap]
    
    return layers