from typing import Optional

from azure.devops.connection import Connection
from azure.devops.v7_0.work import TeamContext, WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItem, WorkItemTrackingClient
from msrest.authentication import BasicAuthentication

# work item fields
WI_ID_KEY = 'System.Id'
WI_TITLE_KEY = 'System.Title'
WI_PRIORITY_KEY = 'Microsoft.VSTS.Common.Priority'
WI_ITEM_TYPE_KEY = 'System.WorkItemType'
WI_ITERATION_PATH_KEY = 'System.IterationPath'
WI_STORY_POINTS_KEY = 'Microsoft.VSTS.Scheduling.StoryPoints'
WI_ASSIGNED_TO_KEY = 'System.AssignedTo'
WI_STATE_KEY = 'System.State'

WI_RELATIONS = 'Relations'
WI_PARENT_RELATION = 'System.LinkTypes.Hierarchy-Reverse'
WI_CHILD_RELATION = 'System.LinkTypes.Hierarchy-Forward'

# work item types
WI_EPIC_TYPE = 'Epic'
WI_FEATURE_TYPE = 'Feature'
WI_USER_STORY_TYPE = 'User Story'
WI_USER_STORY_TYPE_2 = 'Story'
WI_BUG_TYPE = 'Bug'


# backlog categories
BACKLOG_EPIC_CATEGORY = 'Microsoft.EpicCategory'
BACKLOG_FEATURE_CATEGORY = 'Microsoft.FeatureCategory'
BACKLOG_REQUIREMENT_CATEGORY = 'Microsoft.RequirementCategory'
ORDERED_BACKLOG_CATEGORIES = (
    BACKLOG_EPIC_CATEGORY,
    BACKLOG_FEATURE_CATEGORY,
    BACKLOG_REQUIREMENT_CATEGORY,
)


BACKLOG_CATEGORY_WORK_ITEM_TYPE_MAP = {
    BACKLOG_EPIC_CATEGORY.lower(): (WI_EPIC_TYPE,),
    BACKLOG_FEATURE_CATEGORY.lower(): (WI_FEATURE_TYPE,),
    BACKLOG_REQUIREMENT_CATEGORY.lower(): (WI_USER_STORY_TYPE, WI_BUG_TYPE),
}

BACKLOG_WORK_ITEM_TYPE_CATEGORY_MAP = {
    WI_EPIC_TYPE.lower(): BACKLOG_EPIC_CATEGORY,
    WI_FEATURE_TYPE.lower(): BACKLOG_FEATURE_CATEGORY,
    WI_USER_STORY_TYPE.lower(): BACKLOG_REQUIREMENT_CATEGORY,
    WI_USER_STORY_TYPE_2.lower(): BACKLOG_REQUIREMENT_CATEGORY,
    WI_BUG_TYPE.lower(): BACKLOG_REQUIREMENT_CATEGORY,
}


WORK_ITEM_CACHE: dict[int, WorkItem] = {}
BACKLOG_WORK_ITEMS_CACHE: dict[tuple[str, str], list[WorkItem]] = {}


def clear_caches():
    WORK_ITEM_CACHE.clear()
    BACKLOG_WORK_ITEMS_CACHE.clear()


def create_connection(
    organization_url: str, token_password: str, user: Optional[str] = None
) -> Connection:
    user = user if user else ''
    credentials = BasicAuthentication(username=user, password=token_password)
    connection = Connection(base_url=organization_url, creds=credentials)
    return connection


def get_work_item_tracking_client(connection: Connection) -> WorkItemTrackingClient:
    return connection.clients.get_work_item_tracking_client()


def get_work_client(connection: Connection) -> WorkClient:
    return connection.clients.get_work_client()


def get_backlog_category_from_work_item_type(work_item_type: str) -> str:
    return BACKLOG_WORK_ITEM_TYPE_CATEGORY_MAP[work_item_type.lower()]


def get_work_item_types_from_backlog_category(backlog_category: str) -> tuple[str, ...]:
    return BACKLOG_CATEGORY_WORK_ITEM_TYPE_MAP[backlog_category.lower()]


def get_parent_backlog_categories(backlog_category: str) -> tuple[str, ...]:
    return ORDERED_BACKLOG_CATEGORIES[
        : ORDERED_BACKLOG_CATEGORIES.index(backlog_category)
    ]


def get_work_item(
    work_item_id: int, wit_client: WorkItemTrackingClient, force_api: bool = False
) -> WorkItem:
    if not force_api and work_item_id in WORK_ITEM_CACHE:
        return WORK_ITEM_CACHE[work_item_id]

    work_item = wit_client.get_work_item(id=work_item_id, expand=WI_RELATIONS)
    WORK_ITEM_CACHE[work_item_id] = work_item
    return work_item


def get_backlog_work_items(
    backlog_category: str,
    team_context: TeamContext,
    work_client: WorkClient,
    wit_client: WorkItemTrackingClient,
    force_api: bool = False,
) -> list[WorkItem]:
    assert team_context.project, 'Project must be set in team_context'

    cache_key = (team_context.project, backlog_category)
    if not force_api and cache_key in BACKLOG_WORK_ITEMS_CACHE:
        return BACKLOG_WORK_ITEMS_CACHE[cache_key]

    backlog_work_items = work_client.get_backlog_level_work_items(
        team_context=team_context, backlog_id=backlog_category
    ).work_items

    work_item_ids = [wi.target.id for wi in backlog_work_items]
    work_items = wit_client.get_work_items(ids=work_item_ids, expand=WI_RELATIONS)

    BACKLOG_WORK_ITEMS_CACHE[cache_key] = work_items
    WORK_ITEM_CACHE.update({int(wi.id): wi for wi in work_items})

    return work_items


def get_parent_work_item(
    work_item: WorkItem, wit_client: WorkItemTrackingClient
) -> Optional[WorkItem]:
    relations = work_item.relations
    if not relations:
        return None

    for relation in relations:
        if relation.rel == WI_PARENT_RELATION:
            parent_id = int(relation.url.split('/')[-1])
            return get_work_item(parent_id, wit_client)
    return None


def get_children_work_items(
    work_item: WorkItem, wit_client: WorkItemTrackingClient
) -> Optional[list[WorkItem]]:
    relations = work_item.relations
    if not relations:
        return None

    children = []
    for relation in relations:
        if relation.rel == WI_CHILD_RELATION:
            child_id = int(relation.url.split('/')[-1])
            child = get_work_item(child_id, wit_client)
            children.append(child)
    return children


def load_work_items_in_caches(
    team_context: TeamContext,
    work_client: WorkClient,
    wit_client: WorkItemTrackingClient,
) -> None:
    clear_caches()
    for backlog_category in ORDERED_BACKLOG_CATEGORIES:
        _ = get_backlog_work_items(
            backlog_category=backlog_category,
            team_context=team_context,
            work_client=work_client,
            wit_client=wit_client,
        )
