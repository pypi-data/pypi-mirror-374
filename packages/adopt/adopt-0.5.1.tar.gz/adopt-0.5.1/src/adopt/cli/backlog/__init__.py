import click

from adopt.cli.backlog.check import cli_check_backlog
from adopt.cli.backlog.fix import cli_fix_backlog
from adopt.cli.backlog.print import cli_print_backlog
from adopt.cli.backlog.sort import cli_sort_backlog


@click.group(name='backlog', help='Tools to work with the backlog')
def cli_backlog():
    """Root command for all tools working on the backlog."""
    ...


# add each subcommand to the root command
cli_backlog.add_command(cli_print_backlog)
cli_backlog.add_command(cli_sort_backlog)
cli_backlog.add_command(cli_fix_backlog)
cli_backlog.add_command(cli_check_backlog)
