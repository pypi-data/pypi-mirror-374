import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from azure.devops.v7_0.work import TeamContext, WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItem, WorkItemTrackingClient

from adopt.azure_devops import (
    BACKLOG_REQUIREMENT_CATEGORY,
    WI_ASSIGNED_TO_KEY,
    WI_BUG_TYPE,
    WI_EPIC_TYPE,
    WI_FEATURE_TYPE,
    WI_ITEM_TYPE_KEY,
    WI_ITERATION_PATH_KEY,
    WI_PRIORITY_KEY,
    WI_STATE_KEY,
    WI_STORY_POINTS_KEY,
    WI_TITLE_KEY,
    WI_USER_STORY_TYPE,
    get_backlog_category_from_work_item_type,
    get_backlog_work_items,
    get_children_work_items,
    get_parent_work_item,
    get_work_item,
)

LOGGER = logging.getLogger(__name__)


class State(str, Enum):
    NEW = 'New'
    ACTIVE = 'Active'
    RESOLVED = 'Resolved'
    CLOSED = 'Closed'


class BaseWorkItem:
    PARENT_CLASS: type = None
    WORK_ITEM_NAME: str = None

    PRINT_TITLE_LENGTH = 20
    PRINT_PARENT_PATH_SEP = ' > '

    def __init__(
        self,
        work_item: WorkItem,
        wit_client: WorkItemTrackingClient,
        work_client: WorkClient,
        team_context: TeamContext,
    ):
        if work_item.fields[WI_ITEM_TYPE_KEY] != self.WORK_ITEM_NAME:
            raise ValueError(
                f'Work item {work_item.url} is not a {self.WORK_ITEM_NAME}'
            )

        self._work_item = work_item
        self._wit_client = wit_client
        self._work_client = work_client
        self._team_context = team_context

        self._parent = None
        self._children = None
        self._own_backlog_rank = None

    def update(self):
        wi = get_work_item(self.id, self._wit_client, force_api=True)
        self._work_item = wi
        self._parent = None
        self._children = None
        self._own_backlog_rank = None

    @property
    def azure_work_item(self) -> WorkItem:
        return self._work_item

    @property
    def id(self) -> int:
        assert self._work_item.id is not None
        return int(self._work_item.id)

    @property
    def title(self) -> str:
        return self._get_field(WI_TITLE_KEY)

    @property
    def _normalized_title(self) -> Optional[str]:
        title = self.title

        if not title:
            return None

        if len(title) > self.PRINT_TITLE_LENGTH:
            title = title[: self.PRINT_TITLE_LENGTH - 3] + '...'
        return f'{title: <{self.PRINT_TITLE_LENGTH}}'

    @property
    def item_type(self) -> str:
        return self._get_field(WI_ITEM_TYPE_KEY)

    @property
    def iteration_path(self) -> str:
        return self._get_field(WI_ITERATION_PATH_KEY)

    @property
    def assigned_to(self) -> Optional[str]:
        return self._get_field(WI_ASSIGNED_TO_KEY)

    @property
    def state(self) -> str:
        return self._get_field(WI_STATE_KEY)

    @property
    def story_points(self) -> int:
        return self._get_field(WI_STORY_POINTS_KEY)

    @property
    def priority(self) -> int:
        return self._get_field(WI_PRIORITY_KEY)

    @property
    def parent(self) -> Optional['BaseWorkItem']:
        return self._get_parent()

    @property
    def children(self) -> Optional[list['BaseWorkItem']]:
        return self._get_children()

    @property
    def backlog_rank(self) -> Optional[int]:
        if self._own_backlog_rank is None:
            backlog_category = get_backlog_category_from_work_item_type(
                self.WORK_ITEM_NAME
            )
            self._own_backlog_rank = get_work_item_backlog_rank(
                work_item=self._work_item,
                wit_client=self._wit_client,
                work_client=self._work_client,
                team_context=self._team_context,
                backlog_category=backlog_category,
            )
        return self._own_backlog_rank

    @property
    def hierarchy(self) -> tuple['BaseWorkItem', ...]:
        if self.parent is None:
            return (self,)
        return (*self.parent.hierarchy, self)

    def _get_field(self, field_name: str):
        assert self._work_item.fields is not None
        return self._work_item.fields.get(field_name, None)

    def _get_parent(self):
        if self._parent is not None:
            return self._parent

        wi = get_parent_work_item(self._work_item, self._wit_client)
        if not wi:
            return None

        self._parent = self.PARENT_CLASS(
            work_item=wi,
            wit_client=self._wit_client,
            work_client=self._work_client,
            team_context=self._team_context,
        )
        return self._parent

    def _get_children(self):
        if self._children is not None:
            return self._children

        children = get_children_work_items(self._work_item, self._wit_client)
        if children is None:
            return None

        self._children = [
            create_work_item_model(
                work_item=child,
                wit_client=self._wit_client,
                work_client=self._work_client,
                team_context=self._team_context,
            )
            for child in children
        ]
        return self._children

    def __eq__(self, value):
        return self.id == value.id

    def __str__(self) -> str:
        titles = [item.title for item in self.hierarchy]
        title_path = self.PRINT_PARENT_PATH_SEP.join(titles)
        return f'[{self.id}] {self._normalized_title} | {self.iteration_path} | {title_path}'

    def __repr__(self):
        return str(self)


class Epic(BaseWorkItem):
    PARENT_CLASS = BaseWorkItem
    WORK_ITEM_NAME = WI_EPIC_TYPE


class Feature(BaseWorkItem):
    PARENT_CLASS = Epic
    WORK_ITEM_NAME = WI_FEATURE_TYPE


class UserStory(BaseWorkItem):
    PARENT_CLASS = Feature
    WORK_ITEM_NAME = WI_USER_STORY_TYPE

    def __str__(self) -> str:
        return f'({self.priority}) {super().__str__()}'


class Bug(BaseWorkItem):
    PARENT_CLASS = Feature
    WORK_ITEM_NAME = WI_BUG_TYPE

    def __str__(self) -> str:
        return f'({self.priority}) {super().__str__()}'


@dataclass
class Backlog:
    work_items: list[BaseWorkItem]

    def update(self):
        for wi in self.work_items:
            wi.update()

    def copy(self):
        return Backlog(list(self.work_items))

    def __iter__(self):
        return iter(self.work_items)

    def __getitem__(self, index):
        return self.work_items[index]

    def __len__(self):
        return len(self.work_items)

    def __eq__(self, other: 'Backlog'):
        return self.work_items == other.work_items

    def __str__(self):
        return '\n'.join(str(wi) for wi in self.work_items)


def get_work_item_backlog_rank(
    work_item: WorkItem,
    wit_client: WorkItemTrackingClient,
    work_client: WorkClient,
    team_context: TeamContext,
    backlog_category: str,
) -> Optional[int]:
    backlog_work_items = get_backlog_work_items(
        backlog_category=backlog_category,
        team_context=team_context,
        work_client=work_client,
        wit_client=wit_client,
    )

    backlog_work_item_ids = [wi.id for wi in backlog_work_items]
    if work_item.id not in backlog_work_item_ids:
        LOGGER.warning(
            f'Work item "{work_item.fields[WI_TITLE_KEY]}" [{work_item.id}] is not in the backlog'
        )
        return None
    return backlog_work_item_ids.index(work_item.id) + 1


def get_current_iteration(work_client: WorkClient, team_context: TeamContext) -> str:
    return work_client.get_team_iterations(team_context=team_context)


def create_team_context(project: str, team: str) -> TeamContext:
    return TeamContext(project=project, team=team)


def create_work_item_model(
    work_item: WorkItem,
    wit_client: WorkItemTrackingClient,
    work_client: WorkClient,
    team_context: TeamContext,
    item_type: Optional[str] = None,
) -> BaseWorkItem:
    if item_type is None:
        assert work_item.fields and WI_ITEM_TYPE_KEY in work_item.fields
        item_type = work_item.fields[WI_ITEM_TYPE_KEY]

    if item_type == WI_USER_STORY_TYPE:
        return UserStory(work_item, wit_client, work_client, team_context)
    elif item_type == WI_BUG_TYPE:
        return Bug(work_item, wit_client, work_client, team_context)
    elif item_type == WI_FEATURE_TYPE:
        return Feature(work_item, wit_client, work_client, team_context)
    elif item_type == WI_EPIC_TYPE:
        return Epic(work_item, wit_client, work_client, team_context)
    else:
        raise ValueError(f'Unknown work item type: {item_type}')


def update_work_item_field(
    work_item: WorkItem,
    wit_client: WorkItemTrackingClient,
    field: str,
    value: str,
    operation: str = 'replace',
) -> None:
    document = [
        {
            'op': operation,
            'path': f'/fields/{field}',
            'value': value,
        }
    ]
    wit_client.update_work_item(document=document, id=work_item.id)


def get_backlog(
    work_client: WorkClient,
    wit_client: WorkItemTrackingClient,
    team_context: TeamContext,
    backlog_category: str = BACKLOG_REQUIREMENT_CATEGORY,
) -> Backlog:
    backlog_work_items = get_backlog_work_items(
        backlog_category=backlog_category,
        team_context=team_context,
        work_client=work_client,
        wit_client=wit_client,
    )

    items = [
        create_work_item_model(
            work_item=wid,
            wit_client=wit_client,
            work_client=work_client,
            team_context=team_context,
            item_type=None,
        )
        for wid in backlog_work_items
    ]
    return Backlog(items)
