import click
import subprocess
from enum import IntEnum

class EchoLevel(IntEnum):
    """
    echo message level enum(int enum)
    """
    SUCCESS = 0X00
    NORMAL = 0x01
    DEBUG = 0X02

ECHO_LEVEL: EchoLevel = EchoLevel.DEBUG
"""
echo message level variable
"""

def set_level(level: str):
    """
    Set the message level.

    Param:
        level: 'success', 'normal' or 'debug', other is 'normal'
    """
    global ECHO_LEVEL
    if level == 'success':
        ECHO_LEVEL = EchoLevel.SUCCESS
    elif level == 'debug':
        ECHO_LEVEL = EchoLevel.DEBUG
    else:
        ECHO_LEVEL = EchoLevel.NORMAL

def success_echo(msg: str):
    """
    Echo successful message

    Param:
        msg - successful message
    """
    if EchoLevel.SUCCESS <= ECHO_LEVEL:
        click.echo(click.style(f'[+] {msg}', fg='green'))

def fail_echo(msg: str):
    """
    Echo failed message

    Param:
        msg - failed message
    """
    if EchoLevel.NORMAL <= ECHO_LEVEL:
        click.echo(click.style(f'[-] {msg}', fg='red'))

def debug_echo(msg: str):
    """
    Echo debug message

    Param:
        msg - debug message
    """
    if EchoLevel.DEBUG <= ECHO_LEVEL:
        click.echo(click.style(f'[*] {msg}', fg='cyan'))

def call_outer(cmd: list[str], timeout: int = 60):
    """
    Call outer process and return outputs

    Param:
        cmd - commands
        timeout - timeout (secs)
    
    Returns:
        standard outputs and error outputs
    """
    process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outputs, errs = process.communicate(timeout=timeout)
    process.kill()
    return outputs, errs