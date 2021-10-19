import click
from pyencrypt.encrypt import  encrypt
from pathlib import Path
from pyencrypt import __version__,__description__
from pyencrypt.generate import generate_aes_key

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

@click.group()
@click.version_option(__version__,'--version',message=VERSION)
@click.help_option('-h','--help')
def cli():
    pass


@cli.command(name='encrypt')
@click.argument('pathname',type=click.Path(exists=True,resolve_path=True))
@click.option('-i','--in-place','delete',default=False,help='make changes to files in place')
@click.option('-k','--key',default=None,help='key',type=click.STRING)
def encrypt_command(pathname,delete,key):
    """Encrypt your python code"""
    if key is None:
        key = generate_aes_key().decode()
        click.echo(f'Your AES key is {key}.')

    p = Path(pathname)
    if p.is_file():
        encrypt([p,],delete,key)
    else:
        files =  list(p.glob('**/*.py'))
        encrypt(files,delete,key)


@cli.command(name='decrypt')
@click.argument('pathname',type=click.Path(exists=True,resolve_path=True))
def decrypt_command(pathname):
    """Decrypt encrypted pye file"""
    pass


if __name__ == '__main__':
    cli()
