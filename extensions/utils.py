def unhexlify(hex_str: str):
    """
    Turn `00:00:00:00` to `b'\\x00\\x00\\x00\\x00'`

    Param:
        hex_str - Hexadecimal strings with colons (:) in them.
    
    Returns:
        bytes array
    """
    return bytes.fromhex(hex_str.replace(':', ''))

def hexlify(bytes_array: bytes):
    """
    Turn `b'\\x00\\x00\\x00\\x00'` to `00:00:00:00`

    Param:
        bytes_array - bytes array
    
    Returns:
        Hexadecimal strings
    """
    return ':'.join(f'{i:02x}' for i in bytes_array)