import click

from adopt.cli.backlog import cli_backlog


@click.group()
def cli_root():
    """Set of pragmatic tools to automate working with Azure Devops."""


# add each subcommand to the root command
cli_root.add_command(cli_backlog)
