# custom category type and option for backlog commands
import click

category_type = click.Choice(['Story', 'Feature', 'Epic'], case_sensitive=False)
category_option = click.option(
    '--category',
    '-c',
    help='Backlog Category',
    default='Story',
    type=category_type,
    required=True,
)
