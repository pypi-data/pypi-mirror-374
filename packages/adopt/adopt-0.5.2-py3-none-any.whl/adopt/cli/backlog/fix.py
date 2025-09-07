import logging

import click

from adopt.azure_devops import (
    create_connection,
    get_work_client,
    get_work_item_tracking_client,
)
from adopt.backlog.fix import fix_backlog_iteration, fix_backlog_state
from adopt.cli.backlog.options import category_option
from adopt.cli.options import (
    CONTEXT_SETTINGS,
    log_option,
    project_option,
    team_option,
    token_option,
    url_option,
)
from adopt.logging import configure_logging, convert_logging_level
from adopt.work_items import (
    create_team_context,
    get_backlog_category_from_work_item_type,
)

LOGGER = logging.getLogger(__name__)

fix_all_option = click.option('--fix-all', help='Fix all inconsistencies', is_flag=True)
fix_state_option = click.option(
    '--fix-state', help='Fix state inconsistencies', is_flag=True
)
fix_iteration_option = click.option(
    '--fix-iteration', help='Fix iteration inconsistencies', is_flag=True
)
close_option = click.option(
    '--allow-close', help='Allow to close work items', is_flag=True
)


@click.command(
    name='fix',
    help='Fix inconsistencies in the backlog',
    context_settings=CONTEXT_SETTINGS,
)
@url_option
@token_option
@project_option
@team_option
@category_option
@fix_all_option
@fix_state_option
@fix_iteration_option
@close_option
@log_option
def cli_fix_backlog(
    url: str,
    token: str,
    project: str,
    team: str,
    category: str,
    fix_all: bool,
    fix_state: bool,
    fix_iteration: bool,
    allow_close: bool,
    log_level: str,
):
    log_level = convert_logging_level(log_level)
    configure_logging(level=log_level, exclude_external_logs=True)

    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type=category)

    if fix_all or fix_state:
        LOGGER.info('Fixing state inconsistencies')
        fix_backlog_state(
            wit_client=wit_client,
            work_client=work_client,
            team_context=team_context,
            backlog_category=category,
            update_self=True,  # leave for now, expose if necessary
            allow_to_close=allow_close,
        )

    if fix_all or fix_iteration:
        LOGGER.info('Fixing iteration inconsistencies')
        fix_backlog_iteration(
            wit_client=wit_client,
            work_client=work_client,
            team_context=team_context,
            backlog_category=category,
        )
