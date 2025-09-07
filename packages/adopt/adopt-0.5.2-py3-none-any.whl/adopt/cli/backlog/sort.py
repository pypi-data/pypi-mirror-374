import click

from adopt.azure_devops import (
    create_connection,
    get_work_client,
    get_work_item_tracking_client,
)
from adopt.backlog.sort import DEFAULT_SORT_KEY, VALID_SORT_KEY_STR, sort_backlog
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

sort_option = click.option(
    '--sort_key',
    help=f'Sort key [{VALID_SORT_KEY_STR}]',
    default=DEFAULT_SORT_KEY,
    required=True,
)


@click.command(name='sort', help='Sort the backlog', context_settings=CONTEXT_SETTINGS)
@url_option
@token_option
@project_option
@team_option
@category_option
@sort_option
@log_option
def cli_sort_backlog(
    url: str,
    token: str,
    project: str,
    team: str,
    category: str,
    sort_key: str,
    log_level: str,
):
    log_level_int = convert_logging_level(log_level)
    configure_logging(level=log_level_int, exclude_external_logs=True)

    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type=category)

    sort_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
        sort_key=sort_key,
    )
