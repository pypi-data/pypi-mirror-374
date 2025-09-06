from prettytable import PrettyTable

from adopt.work_items import Backlog


# TODO: determine columns from key similar to sort
def format_backlog_as_table(backlog: Backlog) -> str:
    table = PrettyTable()
    table.field_names = [
        'Rank',
        'Title',
        'Id',
        'Iteration Path',
        'Priority',
        'Assigned To',
        'Story Points',
    ]
    for i, item in enumerate(backlog):
        table.add_row(
            [
                i,
                item.title,
                item.id,
                item.iteration_path,
                item.priority,
                item.assigned_to,
                item.story_points,
            ]
        )
    return table.get_string()
