import logging

import click

from adopt.azure_devops import (
    create_connection,
    get_work_client,
    get_work_item_tracking_client,
)
from adopt.backlog.check import (
    check_all_items_assigned,
    check_all_items_have_points,
    check_if_all_items_have_parent,
)
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

check_all = click.option('--check-all', help='Check for all issues', is_flag=True)
check_parent = click.option(
    '--check-parent', help='Check if all items are assigned', is_flag=True
)
check_assigned = click.option(
    '--check-assigned', help='Check if all items are assigned', is_flag=True
)
check_points = click.option(
    '--check-points', help='Check if all items have story points', is_flag=True
)


@click.command(
    name='check',
    help='Check for issues in the backlog',
    context_settings=CONTEXT_SETTINGS,
)
@url_option
@token_option
@project_option
@team_option
@category_option
@check_all
@check_parent
@check_assigned
@check_points
@log_option
def cli_check_backlog(
    url: str,
    token: str,
    project: str,
    team: str,
    category: str,
    check_all: bool,
    check_parent: bool,
    check_assigned: bool,
    check_points: bool,
    log_level: str,
):
    log_level = convert_logging_level(log_level)
    configure_logging(level=log_level, exclude_external_logs=True)

    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type=category)

    if check_all or check_parent:
        LOGGER.info('Checking if all items have a parent')
        check_if_all_items_have_parent(
            wit_client=wit_client,
            work_client=work_client,
            team_context=team_context,
            backlog_category=category,
        )

    if check_all or check_assigned:
        LOGGER.info('Checking if all items are assigned')
        check_all_items_assigned(
            wit_client=wit_client,
            work_client=work_client,
            team_context=team_context,
            backlog_category=category,
        )

    if check_all or check_points:
        LOGGER.info('Checking if all items have story points')
        check_all_items_have_points(
            wit_client=wit_client,
            work_client=work_client,
            team_context=team_context,
            backlog_category=category,
        )
