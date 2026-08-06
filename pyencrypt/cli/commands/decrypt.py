import os
import shutil
from pathlib import Path

import click

from pyencrypt.cli.messages import FINISH_DECRYPT_MSG
from pyencrypt.cli.types import CustomParamType
from pyencrypt.decrypt import decrypt_file


@click.command(name="decrypt")
@click.argument("pathname", type=click.Path(exists=True, resolve_path=True))
@click.option(
    "-i",
    "--in-place",
    "replace",
    default=False,
    help="make changes to files in place",
    is_flag=True,
)
@click.option(
    "-k", "--key", required=True, help="Your encryption key.", type=CustomParamType.KEY
)
@click.help_option("-h", "--help")
@click.pass_context
def decrypt_command(ctx, pathname, replace, key):
    """Decrypt encrypted pye file"""
    path = Path(pathname)

    if path.is_file():
        if replace:
            new_path = path.with_suffix(".py")
        else:
            new_path = Path(os.getcwd()) / path.with_suffix(".py").name
        work_dir = new_path.parent
        origin_data = decrypt_file(path, key, replace, new_path)
        print(origin_data.decode())
    elif path.is_dir():
        if replace:
            work_dir = path
        else:
            work_dir = Path(os.getcwd()) / "decrypted" / path.name
            work_dir.exists() and shutil.rmtree(work_dir)
            shutil.copytree(path, work_dir)
        files = list(work_dir.glob("**/*.pye"))
        with click.progressbar(files, label="🔓 Decrypting") as bar:
            for file in bar:
                new_path = file.with_suffix(".py")
                decrypt_file(file, key, True, new_path)
    else:
        raise Exception(f"{path} is not a valid path.")

    click.echo(FINISH_DECRYPT_MSG.format(work_dir=work_dir))
