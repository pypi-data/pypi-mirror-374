import click

from adopt.cli.backlog import cli_backlog


@click.group()
def cli_root():
    """Root CLI group to hold all subcommands."""


# add each subcommand to the root command
cli_root.add_command(cli_backlog)
