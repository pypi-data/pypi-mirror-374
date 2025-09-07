import logging

from azure.devops.v7_0.work import TeamContext, WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItemTrackingClient

from adopt.work_items import BACKLOG_REQUIREMENT_CATEGORY, get_backlog

LOGGER = logging.getLogger(__name__)


def check_all_items_assigned(
    wit_client: WorkItemTrackingClient,
    work_client: WorkClient,
    team_context: TeamContext,
    backlog_category: str = BACKLOG_REQUIREMENT_CATEGORY,
) -> None:
    """Check if all items in the backlog are assigned to someone."""
    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=backlog_category,
    )

    for item in backlog:
        if not item.assigned_to:
            LOGGER.error(f'{item.item_type} [{item.id}] {item.title} is not assigned')


def check_all_items_have_points(
    wit_client: WorkItemTrackingClient,
    work_client: WorkClient,
    team_context: TeamContext,
    backlog_category: str = BACKLOG_REQUIREMENT_CATEGORY,
) -> None:
    """Check if all items in the backlog are assigned to someone."""
    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=backlog_category,
    )

    for item in backlog:
        if not item.story_points:
            LOGGER.error(
                f'{item.item_type} [{item.id}] {item.title} does not have story points'
            )


def check_if_all_items_have_parent(
    wit_client: WorkItemTrackingClient,
    work_client: WorkClient,
    team_context: TeamContext,
    backlog_category: str = BACKLOG_REQUIREMENT_CATEGORY,
) -> None:
    """Check if all items in the backlog have a parent."""
    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=backlog_category,
    )

    for item in backlog:
        if not item.parent:
            LOGGER.error(
                f'{item.item_type} [{item.id}] {item.title} does not have a parent'
            )
