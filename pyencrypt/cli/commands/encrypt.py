import os
import shutil
import time
from pathlib import Path

import click

from pyencrypt.cli.constants import DATETIME_FORMATS, ENVVAR_PREFIX
from pyencrypt.cli.messages import (
    ENCRYPT_SUMMARY_MSG,
    FINISH_ENCRYPT_MSG,
    FINISH_ENCRYPT_WITH_LOADER_MSG,
    FINISH_GENERATE_LICENSE_MSG,
    INVALID_DATETIME_MSG,
    KEY_OPTION_HELP,
)
from pyencrypt.cli.types import CustomParamType
from pyencrypt.encrypt import can_encrypt, encrypt_file, encrypt_key, generate_so_file
from pyencrypt.generate import generate_aes_key
from pyencrypt.license import MAX_DATETIME, MIN_DATETIME, generate_license_file
from pyencrypt.utils import format_size


@click.command(name="encrypt")
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
    "-k",
    "--key",
    default=None,
    help=KEY_OPTION_HELP,
    type=CustomParamType.KEY,
    envvar=f"{ENVVAR_PREFIX}_KEY",
    show_envvar=True,
)
@click.option(
    "--without-loader",
    default=False,
    help="Don't generate loader file",
    is_flag=True,
)
@click.option(
    "--with-license", default=False, help="Add license to encrypted file", is_flag=True
)
@click.option(
    "-m",
    "--bind-mac",
    "mac",
    default=None,
    help="Bind mac address to encrypted file",
    type=CustomParamType.MAC_ADDR,
)
@click.option(
    "-4",
    "--bind-ipv4",
    "ipv4",
    default=None,
    help="Bind ipv4 address to encrypted file",
    type=CustomParamType.IPV4_ADDR,
)
@click.option(
    "-b",
    "--before",
    default=MIN_DATETIME,
    help="License is invalid before this date.",
    type=click.DateTime(formats=DATETIME_FORMATS),
)
@click.option(
    "-a",
    "--after",
    default=MAX_DATETIME,
    help="License is invalid after this date.",
    type=click.DateTime(formats=DATETIME_FORMATS),
)
@click.confirmation_option(
    "-y",
    "--yes",
    prompt="Are you sure you want to encrypt your python file?",
    help="Automatically answer yes for confirm questions.",
)
@click.help_option("-h", "--help")
@click.pass_context
def encrypt_command(
    ctx, pathname, replace, key, without_loader, with_license, mac, ipv4, before, after
):
    """Encrypt your python code"""
    if key is None:
        key = generate_aes_key().decode()
        click.echo(
            f'Your randomly encryption 🔑 is {click.style(key, underline=True, fg="yellow")}'
        )

    if before > after:
        ctx.fail(INVALID_DATETIME_MSG)

    path = Path(pathname)

    if path.is_file():
        if replace:
            new_path = path.with_suffix(".pye")
        else:
            new_path = Path(os.getcwd()) / path.with_suffix(".pye").name
        encrypt_file(path, key, replace, new_path)
    elif path.is_dir():
        if replace:
            work_dir = path
        else:
            work_dir = Path(os.getcwd()) / "encrypted" / path.name
            work_dir.exists() and shutil.rmtree(work_dir)
            shutil.copytree(path, work_dir)
        files = set(work_dir.glob("**/*.py"))
        count = 0
        total_size = 0
        start = time.perf_counter()
        with click.progressbar(files, label="🔐 Encrypting") as bar:
            for file in bar:
                new_path = file.with_suffix(".pye")
                if can_encrypt(file):
                    total_size += file.stat().st_size
                    encrypt_file(file, key, True, new_path)
                    count += 1
        elapsed = time.perf_counter() - start
        click.echo(
            ENCRYPT_SUMMARY_MSG.format(
                count=count, size=format_size(total_size), elapsed=elapsed
            )
        )
    else:
        raise Exception(f"{path} is not a valid path.")

    if with_license is True:
        generate_license_file(key, Path(os.getcwd()), after, before, mac, ipv4)
        click.echo(FINISH_GENERATE_LICENSE_MSG)

    if without_loader is True:
        click.echo(FINISH_ENCRYPT_MSG)
        return

    cipher_key, d, n = encrypt_key(key.encode())  # 需要放进导入器中
    loader_extension = generate_so_file(cipher_key, d, n, license=with_license)
    click.echo(FINISH_ENCRYPT_WITH_LOADER_MSG.format(loader_extension.name))
