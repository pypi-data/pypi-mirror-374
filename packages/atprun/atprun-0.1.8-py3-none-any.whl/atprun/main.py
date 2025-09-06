# https://typer.tiangolo.com/tutorial/package/

from pprint import pprint

import typer

from .configuration import AtpRunMain

app: typer.Typer = typer.Typer()
atprunconfig: AtpRunMain = AtpRunMain()


@app.callback()
def callback(
    config_path: str | None = typer.Option(
        default=None,
        help="Configuration file path",
    ),
):
    """
    AtpRun
    """
    print("callback", "Start")
    print("config_path", config_path)
    # load config file
    atprunconfig.load_configuration(path=config_path)
    print("callback", "End")
    pass


@app.command()
def script(
    name: str,
):
    """
    Run script
    """
    try:
        atprunconfig.script_run(name=name)
    except ValueError as err:
        typer.secho(
            f"Error: {err}",
            err=True,
            fg=typer.colors.RED,
        )
    except Exception as err:
        typer.secho(
            f"Error [Unexpected]: {err}",
            err=True,
            fg=typer.colors.RED,
        )


if __name__ == "__main__":
    app()
