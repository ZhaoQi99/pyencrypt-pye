import click


@click.command(name="gui")
@click.help_option("-h", "--help")
def gui_command():
    """Launch the graphical interface."""
    try:
        from pyencrypt.gui import run
    except ImportError as exc:
        raise click.ClickException(str(exc))
    run()
