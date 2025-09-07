import pytest

from adopt.azure_devops import (
    create_connection,
    get_work_client,
    get_work_item_tracking_client,
)
from adopt.backlog.fix import fix_backlog_state
from adopt.work_items import (
    create_team_context,
    get_backlog_category_from_work_item_type,
)


@pytest.mark.mutate
def test_azure_backlog_state(url, token, project, team):
    # TODO: get a specific work item and change the type, then check the parent
    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type='story')

    fix_backlog_state(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
        update_self=True,
        allow_to_close=True,
    )
