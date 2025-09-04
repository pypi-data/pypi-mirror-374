import typer

from charsi.__about__ import __version__
from charsi.commands import imbue

app = typer.Typer(no_args_is_help=True)
app.command(name='imbue')(imbue.imbue_command)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    _: bool = typer.Option(
        None,
        '--version',
        help='Print version',
        callback=version_callback,
        is_eager=True,
        expose_value=False,
    )
):
    """
    A command-line tool to help game modders build string resources for Diablo II: Resurrected.
    """


if __name__ == '__main__':
    app()
