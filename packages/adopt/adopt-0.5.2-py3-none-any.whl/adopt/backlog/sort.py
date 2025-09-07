import logging
import re
from dataclasses import dataclass
from functools import cmp_to_key, partial
from typing import Optional

from azure.devops.v7_0.work import ReorderOperation, TeamContext, WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItemTrackingClient
from contexttimer import timer

from adopt.azure_devops import load_work_items_in_caches
from adopt.work_items import (
    BACKLOG_REQUIREMENT_CATEGORY,
    Backlog,
    BaseWorkItem,
    get_backlog,
)

LOGGER = logging.getLogger(__name__)

VALID_SORT_KEY_ELEMENTS = [
    'i',  # iteration path
    'p',  # priority
    't',  # title
    'r',  # rank
]
VALID_SORT_KEY_ELEMENTS_ALL = [
    val for el in VALID_SORT_KEY_ELEMENTS for val in (el, el.upper())
]
VALID_SORT_KEY_STR = (
    ', '.join(VALID_SORT_KEY_ELEMENTS_ALL[:-1])
    + f' or {VALID_SORT_KEY_ELEMENTS_ALL[-1]}'
)
VALID_SORT_KEY_REGEX = re.compile(rf'^[{"".join(VALID_SORT_KEY_ELEMENTS_ALL)}]+$')

DEFAULT_SORT_KEY = 'Iprt'

MAX_RANK = 1e3


@dataclass
class Swap:
    item: BaseWorkItem
    next_item: Optional[BaseWorkItem]
    previous_item: Optional[BaseWorkItem]

    def __str__(self) -> str:
        prev_item, next_item = self.previous_item, self.next_item
        after_text = f'after "{prev_item.title}"' if prev_item else 'at the beginning'
        before_text = f'before "{next_item.title}"' if next_item else 'at the end'
        return f'"{self.item.title}" {after_text} and {before_text}'

    @property
    def item_id(self) -> int:
        return self.item.id

    @property
    def next_id(self) -> int:
        return self.next_item.id if self.next_item else 0

    @property
    def previous_id(self) -> int:
        return self.previous_item.id if self.previous_item else 0


def _validate_sort_key(sort_key: str):
    if not VALID_SORT_KEY_REGEX.match(sort_key):
        raise ValueError(
            f'Invalid sort key "{sort_key}". Must be a combination of {VALID_SORT_KEY_STR}'
        )
    if len(set(sort_key.lower())) != len(sort_key.lower()):
        raise ValueError(f'Duplicate sort key elements in "{sort_key}"')


def _compare_attr(
    item1: BaseWorkItem, item2: BaseWorkItem, attr: str, ascending: bool
) -> int:
    item1_attr = getattr(item1, attr)
    item2_attr = getattr(item2, attr)

    if item1_attr == item2_attr:
        return 0

    value = -1 if item1_attr < item2_attr else 1
    if not ascending:
        value *= -1

    return value


def _compare_rank(item1: BaseWorkItem, item2: BaseWorkItem, ascending: bool) -> int:
    item1_parents_rank = [item.backlog_rank for item in item1.hierarchy]
    item2_parents_rank = [item.backlog_rank for item in item2.hierarchy]

    # if a parent has no rank, we consider it to be at the end of the backlog
    item1_parents_rank = [
        rank if rank is not None else MAX_RANK for rank in item1_parents_rank
    ]
    item2_parents_rank = [
        rank if rank is not None else MAX_RANK for rank in item2_parents_rank
    ]

    if item1_parents_rank == item2_parents_rank:
        return 0

    value = -1 if item1_parents_rank < item2_parents_rank else 1
    if not ascending:
        value *= -1

    return value


def compare_work_items(item1: BaseWorkItem, item2: BaseWorkItem, sort_key: str) -> int:
    _validate_sort_key(sort_key)

    result = 0
    for key in sort_key:
        ascending = key.islower()
        key = key.lower()

        if key == 'i':
            result = _compare_attr(
                item1, item2, attr='iteration_path', ascending=ascending
            )
        elif key == 'p':
            result = _compare_attr(item1, item2, attr='priority', ascending=ascending)
        elif key == 'r':
            result = _compare_rank(item1, item2, ascending=ascending)
        elif key == 't':
            result = _compare_attr(item1, item2, attr='title', ascending=ascending)
        else:
            raise ValueError(f'Invalid sort key "{key}"')

        # keep comparing until we find a difference
        if result != 0:
            return result
    return result


def generate_sort_key_func(sort_key: str):
    return cmp_to_key(partial(compare_work_items, sort_key=sort_key))


@timer(logger=LOGGER, level=logging.INFO, fmt='Sorted backlog in %(execution_time).2fs')
def sort_backlog(
    wit_client: WorkItemTrackingClient,
    work_client: WorkClient,
    team_context: TeamContext,
    backlog_category: str = BACKLOG_REQUIREMENT_CATEGORY,
    sort_key: str = DEFAULT_SORT_KEY,
) -> Backlog:
    # load all work items in cache to avoid multiple calls to the server
    load_work_items_in_caches(
        team_context=team_context, work_client=work_client, wit_client=wit_client
    )

    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=backlog_category,
    )

    LOGGER.debug('Current backlog:')
    for item in backlog:
        LOGGER.debug(item)

    key_func = generate_sort_key_func(sort_key=sort_key)
    sorted_work_items = sorted(backlog.work_items, key=key_func)
    sorted_backlog = Backlog(sorted_work_items)

    LOGGER.debug('Sorted backlog:')
    for item in sorted_backlog:
        LOGGER.debug(item)

    is_in_order = backlog == sorted_backlog
    if is_in_order:
        LOGGER.info('all user stories are in correct order')
        return backlog
    return backlog
    LOGGER.info('user stories are not in the correct order')
    reorder_backlog(
        backlog=backlog,
        target_backlog=sorted_backlog,
        work_client=work_client,
        team_context=team_context,
    )

    new_backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=backlog_category,
    )
    LOGGER.debug('New backlog:')
    for item in new_backlog:
        LOGGER.debug(item)

    assert new_backlog == sorted_backlog
    return new_backlog


def reorder_backlog(
    backlog: Backlog,
    target_backlog: Backlog,
    work_client: WorkClient,
    team_context: TeamContext,
) -> None:
    swaps = _compute_swaps(backlog=backlog, target=target_backlog)
    for swap in swaps:
        LOGGER.info(f'Apply swap {swap}')
        _apply_swap_on_azure(
            swap=swap, work_client=work_client, team_context=team_context
        )


def reorder_backlog_local(backlog: Backlog, target_backlog: Backlog):
    swaps = _compute_swaps(backlog=backlog, target=target_backlog)
    for swap in swaps:
        LOGGER.info(f'Apply swap {swap}')
        _apply_swap_on_backlog(swap=swap, backlog=backlog)


def _compute_swaps(backlog: Backlog, target: Backlog) -> list[Swap]:
    swaps = []

    current_backlog = backlog.copy()
    for target_item_idx, target_item in enumerate(target.work_items):
        current_items = current_backlog.work_items
        item_on_current_backlog = current_items[target_item_idx]

        if item_on_current_backlog.id == target_item.id:
            continue

        if target_item_idx == 0:
            previous_item = None
            next_item = current_items[target_item_idx]
        elif target_item_idx == len(target) - 1:
            previous_item = current_items[target_item_idx - 1]
            next_item = None
        else:
            previous_item = current_items[target_item_idx - 1]
            next_item = current_items[target_item_idx]

        swap = Swap(item=target_item, next_item=next_item, previous_item=previous_item)
        _apply_swap_on_backlog(swap=swap, backlog=current_backlog)
        swaps.append(swap)

    return swaps


def _apply_swap_on_azure(
    swap: Swap, work_client: WorkClient, team_context: TeamContext
):
    reorder_operation = ReorderOperation(
        ids=[swap.item_id],
        iteration_path=None,
        next_id=swap.next_id,
        previous_id=swap.previous_id,
    )

    work_client.reorder_backlog_work_items(reorder_operation, team_context=team_context)


def _apply_swap_on_backlog(swap: Swap, backlog: Backlog):
    work_items = backlog.work_items
    work_items.remove(swap.item)

    if swap.previous_item is None:
        work_items = [swap.item] + work_items
    elif swap.next_item is None:
        work_items = work_items + [swap.item]
    else:
        prev_item_idx = work_items.index(swap.previous_item)
        next_item_idx = work_items.index(swap.next_item)
        assert prev_item_idx == next_item_idx - 1

        work_items = (
            work_items[: prev_item_idx + 1] + [swap.item] + work_items[next_item_idx:]
        )
    backlog.work_items = work_items
