import os
from pathlib import Path

import click

from pyencrypt.cli.messages import (
    DATETIME_FORMATS,
    FINISH_GENERATE_LICENSE_MSG,
    INVALID_DATETIME_MSG,
)
from pyencrypt.cli.types import CustomParamType
from pyencrypt.license import MAX_DATETIME, MIN_DATETIME, generate_license_file


@click.command(name="license")
@click.help_option("-h", "--help")
@click.option(
    "-k", "--key", required=True, help="Your encryption key.", type=CustomParamType.KEY
)
@click.option(
    "-m",
    "--bind-mac",
    "mac",
    default=None,
    help="Your mac address.",
    type=CustomParamType.MAC_ADDR,
)
@click.option(
    "-4",
    "--bind-ipv4",
    "ipv4",
    default=None,
    help="Your ipv4 address.",
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
@click.pass_context
def generate_license(ctx, key, mac, ipv4, before, after):
    """Generate license file using specified key"""
    if before > after:
        ctx.fail(INVALID_DATETIME_MSG)

    generate_license_file(key, Path(os.getcwd()), after, before, mac, ipv4)
    click.echo(FINISH_GENERATE_LICENSE_MSG)
