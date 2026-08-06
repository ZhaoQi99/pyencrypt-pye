import click

from pyencrypt import __version__
from pyencrypt.cli.commands.decrypt import decrypt_command
from pyencrypt.cli.commands.encrypt import encrypt_command
from pyencrypt.cli.commands.gui import gui_command
from pyencrypt.cli.commands.license import generate_license
from pyencrypt.cli.commands.loader import generate_loader
from pyencrypt.cli.messages import VERSION


@click.group()
@click.version_option(__version__, "-V", "--version", message=VERSION)
@click.help_option("-h", "--help")
def cli():
    pass


cli.add_command(encrypt_command)
cli.add_command(decrypt_command)
cli.add_command(generate_loader)
cli.add_command(generate_license)
cli.add_command(gui_command)


if __name__ == "__main__":
    cli()
