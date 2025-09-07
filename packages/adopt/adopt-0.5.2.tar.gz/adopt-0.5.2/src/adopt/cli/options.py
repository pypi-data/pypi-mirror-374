import click

from adopt.config import ADO_ORG_URL_VAR, ADO_PAT_VAR, ADO_PROJECT_VAR, ADO_TEAM_VAR

# add -h to trigger help
CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}

# custom choice type for log levels
log_type = click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False
)

# common options for all subcommands
url_option = click.option(
    '--url', help='Organization URL', envvar=ADO_ORG_URL_VAR, required=True
)
token_option = click.option(
    '--token', help='Personal Access Token', envvar=ADO_PAT_VAR, required=True
)
project_option = click.option(
    '--project', help='Project Name', envvar=ADO_PROJECT_VAR, required=True
)
team_option = click.option(
    '--team', help='Team Name', envvar=ADO_TEAM_VAR, required=True
)
log_option = click.option(
    '--log-level', help='Log Level', default='INFO', type=log_type, required=True
)
