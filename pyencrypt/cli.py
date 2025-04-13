import base64
import ipaddress
import os
import re
import shutil
import sys
from pathlib import Path

import click
from click.core import ParameterSource  # click>=8

from pyencrypt import __description__, __version__
from pyencrypt.decrypt import decrypt_file
from pyencrypt.encrypt import can_encrypt, encrypt_file, encrypt_key, generate_so_file
from pyencrypt.generate import generate_aes_key
from pyencrypt.license import MAX_DATETIME, MIN_DATETIME, generate_license_file

VERSION = rf"""
                                                      _
         _ __  _   _  ___ _ __   ___ _ __ _   _ _ __ | |_
        | '_ \| | | |/ _ \ '_ \ / __| '__| | | | '_ \| __|
        | |_) | |_| |  __/ | | | (__| |  | |_| | |_) | |_
        | .__/ \__, |\___|_| |_|\___|_|   \__, | .__/ \__|
        |_|    |___/                      |___/|_|

        {__description__}

                    VERSION {__version__}
"""  # noqa: E221,E222

KEY_OPTION_HELP = """
Your encryption key.If you don't specify key,
pyencrypt will generate encryption key randomly.
"""

PYTHON_MAJOR, PYTHON_MINOR = sys.version_info[:2]
LOADER_FILE_NAME = click.style("encrypted/{}", blink=True, fg="blue")
LICENSE_FILE_NAME = click.style("license.lic", blink=True, fg="blue")

SUCCESS_ANSI = click.style("successfully", fg="green")

INVALID_KEY_MSG = click.style("Your encryption 🔑 is invalid.", fg="red")

INVALID_MAC_MSG = click.style("{} is not a valid mac address.", fg="red")

INVALID_IPV4_MSG = click.style("{} is not a valid ipv4 address.", fg="red")

INVALID_DATETIME_MSG = click.style(
    "Before date must be less than after date.", fg="red"
)

FINISH_ENCRYPT_MSG = f"""
Encryption completed {SUCCESS_ANSI}.
Please copy {LOADER_FILE_NAME} into your encrypted directory.
And then remove `encrypted` directory.
Finally, add `import loader` at the top of your entry file.\n
"""  # noqa: W604

FINISH_DECRYPT_MSG = f"""
Decryption completed {SUCCESS_ANSI}. Your origin source code has be put: {{work_dir}}
"""

FINISH_GENERATE_LOADER_MSG = f"""
Generate loader file {SUCCESS_ANSI}. Your loader file is located in {LOADER_FILE_NAME}
"""

FINISH_GENERATE_LICENSE_MSG = f"""
Generate license file {SUCCESS_ANSI}. Your license file is located in {LICENSE_FILE_NAME}
"""

DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]

ENVVAR_PREFIX = "PYE_ENCRYPT"


class KeyParamType(click.ParamType):
    name = "key"

    def _check_key(self, key: str) -> bool:
        return not (len(key) % 4 or len(base64.b64decode(key)) % 16)

    def convert(self, value, param, ctx) -> str:
        if ctx.get_parameter_source(param.name) == ParameterSource.ENVIRONMENT:
            visible_chars = 4
            masked = (
                value[:visible_chars]
                + "*" * (len(value) - 2 * visible_chars)
                + value[-visible_chars:]
            )
            click.echo(
                f'Using encryption key 🔑 {click.style(masked, fg="yellow")} from environment variable {click.style(param.envvar, fg="bright_cyan")}.'
            )

        value = click.STRING.convert(value, param, ctx)
        if not self._check_key(value):
            self.fail(INVALID_KEY_MSG, param, ctx)
        return value

    def get_metavar(self, param):
        return "🔑"

    def __repr__(self) -> str:
        return "KEY"


class MacAddressParamType(click.ParamType):
    name = "mac_address"
    pattern = re.compile(r"^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$")

    def convert(self, value, param, ctx) -> str:
        value = click.STRING.convert(value, param, ctx)
        if not self.pattern.match(value):
            self.fail(INVALID_MAC_MSG.format(value), param, ctx)
        return value

    def get_metavar(self, param):
        return "01:23:45:67:89:AB"

    def __repr__(self) -> str:
        return "MacAddress"


class IPv4AddressParamType(click.ParamType):
    name = "ipv4_address"

    def convert(self, value, param, ctx) -> str:
        value = click.STRING.convert(value, param, ctx)
        try:
            return str(ipaddress.IPv4Address(value))
        except ValueError:
            self.fail(INVALID_IPV4_MSG.format(value), param, ctx)

    def get_metavar(self, param):
        return "192.168.0.1"

    def __repr__(self) -> str:
        return "Ipv4Address"


class CustomParamType:
    KEY = KeyParamType()
    MAC_ADDR = MacAddressParamType()
    IPV4_ADDR = IPv4AddressParamType()


@click.group()
@click.version_option(__version__, "-V", "--version", message=VERSION)
@click.help_option("-h", "--help")
def cli():
    pass


@cli.command(name="encrypt")
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
    ctx, pathname, replace, key, with_license, mac, ipv4, before, after
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
        with click.progressbar(files, label="🔐 Encrypting") as bar:
            for file in bar:
                new_path = file.with_suffix(".pye")
                if can_encrypt(file):
                    encrypt_file(file, key, True, new_path)
    else:
        raise Exception(f"{path} is not a valid path.")

    cipher_key, d, n = encrypt_key(key.encode())  # 需要放进导入器中
    loader_extension = generate_so_file(cipher_key, d, n, license=with_license)
    if with_license is True:
        generate_license_file(key, Path(os.getcwd()), after, before, mac, ipv4)
        click.echo(FINISH_GENERATE_LICENSE_MSG)
    click.echo(FINISH_ENCRYPT_MSG.format(loader_extension.name))


@cli.command(name="decrypt")
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


@cli.command(name="generate")
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


@cli.command(name="license")
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


if __name__ == "__main__":
    cli()
