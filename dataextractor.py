import pkgutil
import importlib
import click
import hashlib
import os
from extensions import set_level

FILE_SUFFIX = '.qsdz'
"""
Temp file or other's suffix
"""

VERSION = '1.0.0'
"""
DataExtractor version
"""

SCRIPT_NAME = 'DataExtractor'
"""
This script's name
"""

@click.group()
@click.option('-f', '--file', required=True, type=click.Path(exists=True), help='source')
@click.option('-l', '--level', type=click.Choice(['success', 'normal', 'debug']))
@click.version_option(VERSION, '-v', '--version', prog_name=SCRIPT_NAME)
@click.pass_context
def run(ctx: click.Context, file: str, level: str):
    """
    This script helps extract data from traffic files, log files, and various other files.

    —— qsdz (qingsiduzou@gmail.com)
    """
    ctx.ensure_object(dict)
    filepath = os.path.abspath(file)
    # Save context - the full path to the input file
    ctx.obj['filepath'] = filepath
    # Save context - input file directory path
    ctx.obj['filedir'] = os.path.dirname(filepath)
    # Save context - the filename of the input file
    ctx.obj['filename'] = os.path.basename(filepath)

    with open(file, 'rb') as f:
        data = f.read()
        # Save context - the hash of the input file
        ctx.obj['filehash'] = hashlib.sha1(data).hexdigest()
    # Save context - the temporary file name of the input file
    ctx.obj['tmpname'] = ctx.obj['filehash'] + FILE_SUFFIX
    tmppath = os.path.join(os.getenv('TEMP', './'), ctx.obj['tmpname'])
    # If temporary file paths conflict, generate new temporary file paths
    while os.path.exists(tmppath):
        ctx.obj['tmpname'] = hashlib.sha1(ctx.obj['tmpname'].encode()).hexdigest() + FILE_SUFFIX
        tmppath = os.path.join(os.getenv('TEMP', ctx.obj['filedir']), ctx.obj['tmpname'])
    # Save context - temporary directory for input files
    ctx.obj['tmppath'] = tmppath

    ctx.obj['level'] = level
    set_level(level)

if __name__ == '__main__':
    # The path to the plugin module.
    extension_path = "extensions"
    # All the plugin modules.
    extensions = {}
    # Iterate through and import the respective plugins.
    for finder, name, ispkg in pkgutil.iter_modules([extension_path]):
        extensions[name] = importlib.import_module(f'{extension_path}.{name}')
    # All the plugin names.
    extension_names = tuple(extensions.keys())
    for name in extension_names:
        run.add_command(getattr(extensions[name], 'parse', None), name)
    run()