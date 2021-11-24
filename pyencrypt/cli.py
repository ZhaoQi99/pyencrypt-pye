import base64
import os
import shutil
import sys
from pathlib import Path

import click
from pyencrypt import __description__, __version__
from pyencrypt.decrypt import decrypt_file
from pyencrypt.encrypt import (can_encrypt, encrypt_file, encrypt_key,
                               generate_so_file)
from pyencrypt.generate import generate_aes_key
from pyencrypt.check import CheckFinder


VERSION = f"""\
                                                      _
         _ __  _   _  ___ _ __   ___ _ __ _   _ _ __ | |_
        | '_ \| | | |/ _ \ '_ \ / __| '__| | | | '_ \| __|
        | |_) | |_| |  __/ | | | (__| |  | |_| | |_) | |_
        | .__/ \__, |\___|_| |_|\___|_|   \__, | .__/ \__|
        |_|    |___/                      |___/|_|

        {__description__}

                    VERSION {__version__}
"""

KEY_OPTION_HELP = """
Your encryption key.If you don‘t specify key,
pyencrypt will generate encryption key randomly.

"""

PYTHON_MAJOR, PYTHON_MINOR = sys.version_info[:2]
LAODER_FILE_NAME = "loader.cpython-{major}{minor}{abi}-{platform}.so".format(
    major=PYTHON_MAJOR,
    minor=PYTHON_MINOR,
    abi=sys.abiflags,
    platform=sys.platform)

FINISH_ENCRYPT_MSG = f"""
Encryption completed successfully.
Please copy encrypted/{LAODER_FILE_NAME} into your encrypted directory.
And then remove `encrypted` directory.
Finally, add `import loader` at the top of your entry file.\
"""

FINISH_DECRYPT_MSG = """
Decryption completed successfully. Your origin source code has be put: {path}\
"""

FINISH_GENERATE_MSG = f"""
Generate loader file successfully. Your loader file is located in {LAODER_FILE_NAME}
"""


def _check_key(key: str) -> bool:
    return not (len(key) % 4 or len(base64.b64decode(key)) % 16)


@click.group()
@click.version_option(__version__, '--version', message=VERSION)
@click.help_option('-h', '--help')
def cli():
    pass


@cli.command(name='encrypt')
@click.argument('pathname', type=click.Path(exists=True, resolve_path=True))
@click.option('-i',
              '--in-place',
              'delete',
              default=False,
              help='make changes to files in place',
              is_flag=True)
@click.option('-k',
              '--key',
              default=None,
              help=KEY_OPTION_HELP,
              type=click.STRING)
@click.confirmation_option(
    prompt='Are you sure you want to encrypt your python file?',
    help='Automatically answer yes for confirm questions.')
@click.help_option('-h', '--help')
@click.pass_context
def encrypt_command(ctx, pathname, delete, key):
    """Encrypt your python code"""
    if key is not None and not _check_key(key):
        ctx.fail(f'Your encryption key is invalid.')
    if key is None:
        key = generate_aes_key().decode()
        click.echo(f'Your randomly encryption 🔑 is {key}')

    path = Path(pathname)
    work_dir = Path(os.getcwd()) / 'encrypted' / 'src'

    if path.is_file():
        new_path = Path(os.getcwd()) / path.with_suffix('.pye').name
        encrypt_file(path, key, delete, new_path)
    elif path.is_dir():
        work_dir.exists() and shutil.rmtree(work_dir)
        shutil.copytree(path, work_dir)
        files = set(path.glob('**/*.py')) - set(
            path.glob(f'encrypted/**/*.py'))
        with click.progressbar(files, label='🔐 Encrypting') as bar:
            for file in bar:
                if can_encrypt(file):
                    new_path = work_dir / file.relative_to(path)
                    new_path.unlink()
                    encrypt_file(file, key, delete,
                                 new_path.with_suffix('.pye'))
    else:
        raise Exception(f'{path} is not a valid path.')

    cipher_key, d, n = encrypt_key(key.encode())  # 需要放进导入器中
    generate_so_file(cipher_key, d, n)
    click.echo(FINISH_ENCRYPT_MSG)


@cli.command(name='decrypt')
@click.argument('pathname', type=click.Path(exists=True, resolve_path=True))
@click.option('-k',
              '--key',
              required=True,
              help='Your encryption key.',
              type=click.STRING)
@click.help_option('-h', '--help')
def decrypt_command(pathname, key):
    """Decrypt encrypted pye file"""
    path = Path(pathname)

    if path.is_file():
        work_dir = Path(os.getcwd())
        new_path = work_dir / path.with_suffix('.py').name
        origin_data = decrypt_file(path, key, new_path)
        print(origin_data.decode())
    elif path.is_dir():
        work_dir = Path(os.getcwd()) / 'decrypted' / 'src'
        work_dir.exists() and shutil.rmtree(work_dir)
        shutil.copytree(path, work_dir)
        files = list(path.glob('**/*.pye'))
        with click.progressbar(files, label='🔓 Decrypting') as bar:
            for file in files:
                new_path = work_dir / file.relative_to(path)
                decrypt_file(file, key, new_path)
    else:
        raise Exception(f'{path} is not a valid path.')

    click.echo(FINISH_DECRYPT_MSG.format(path=work_dir))


@cli.command(name='generate')
@click.option('-k',
              '--key',
              required=True,
              help='Your encryption key.',
              type=click.STRING)
@click.help_option('-h', '--help')
@click.pass_context
def generate_loader(ctx, key):
    """Generate loader file using specified key"""
    if not _check_key(key):
        ctx.fail(f'Your encryption key is invalid.')
    cipher_key, d, n = encrypt_key(key.encode())
    generate_so_file(cipher_key, d, n)
    click.echo(FINISH_GENERATE_MSG)


@cli.command(name='check')
@click.argument('entry', type=click.Path(exists=True))
@click.help_option('-h', '--help')
def check(entry):
    """Check to see if it can be encrypted"""
    sys.path.insert(0,os.getcwd())
    sys.meta_path.insert(0,CheckFinder())
    entry = Path(entry).as_posix().rstrip('.py').replace('/','.')
    __import__(entry)


if __name__ == '__main__':
    cli()
