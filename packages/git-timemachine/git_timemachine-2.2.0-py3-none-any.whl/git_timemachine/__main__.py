import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
import typer
from packaging import version

from git_timemachine.__about__ import __version__
from git_timemachine.commands import advance, commit, review
from git_timemachine.models import Config, States

app = typer.Typer(no_args_is_help=True)
app.command(name='advance')(advance.advance_command)
app.command(name='commit')(commit.commit_command)
app.command(name='review')(review.review_command)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


def check_update():
    url = 'https://pypi.org/pypi/git-timemachine/json'
    data = requests.get(url).json()
    latest = data['info']['version']

    if version.parse(latest) > version.parse(__version__):
        typer.echo(
            typer.style(f'WARNING: You are using git-timemachine version {__version__}; however, version {latest} is available.', fg=typer.colors.YELLOW)
        )
        typer.echo(
            typer.style('You should consider upgrading via the "pip install --upgrade git-timemachine" command.', fg=typer.colors.YELLOW)
        )
        typer.echo()


@app.callback()
def main(
    ctx: typer.Context,
    repo_dir: Path = typer.Option(Path.cwd(), '--repo-dir', '-C', help='Path of repository directory.', metavar='PATH'),
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
    A command-line tool that helps you record commits on Git repositories at any time node.
    """

    config_file = Path(os.getenv('GIT_TIMEMACHINE_CONFIG', Path.home() / '.git-timemachine' / 'config'))
    states_file = Path(os.getenv('GIT_TIMEMACHINE_STATES', Path.home() / '.git-timemachine' / 'states'))

    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        Config().save(config_file)

    if not states_file.exists():
        states_file.parent.mkdir(parents=True, exist_ok=True)
        States.model_validate({
            'last_commit_time': datetime.now(),
            'last_update_check': datetime.now() - timedelta(days=1)
        }).save(states_file)

    config = Config.load(config_file)
    states = States.load(states_file)

    if datetime.now() - states.last_update_check > timedelta(days=config.update_check_interval):
        check_update()
        states.last_update_check = datetime.now()
        states.save()

    ctx.ensure_object(dict)

    ctx.obj['repo_dir'] = repo_dir
    ctx.obj['config'] = Config.load(config_file)
    ctx.obj['states'] = States.load(states_file)


if __name__ == '__main__':
    app()
