import os
from pathlib import Path

import click

from pyencrypt.cli.messages import FINISH_GENERATE_LOADER_MSG
from pyencrypt.cli.types import CustomParamType
from pyencrypt.encrypt import encrypt_key, generate_so_file


@click.command(name="loader")
@click.option(
    "-k", "--key", required=True, help="Your encryption key.", type=CustomParamType.KEY
)
@click.help_option("-h", "--help")
@click.pass_context
def generate_loader(ctx, key):
    """Generate loader file using specified key"""
    cipher_key, d, n = encrypt_key(key.encode())
    loader_extension = generate_so_file(cipher_key, d, n, Path(os.getcwd()))
    click.echo(FINISH_GENERATE_LOADER_MSG.format(loader_extension.name))
