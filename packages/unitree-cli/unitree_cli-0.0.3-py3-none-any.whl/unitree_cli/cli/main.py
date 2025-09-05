import rich_click as click

from unitree_cli.tools.joystick import joystick
from unitree_dds_wrapper.utils.cli.main import cli as dds

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.COMMAND_GROUPS = {
    "unitree": [
        {
            "name": "Utilities",
            "commands": ["joystick"],
        },
        {
            "name": "cyclonedds tools",
            "commands": ["dds"],
        },
    ]
}

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(name="unitree", context_settings=CONTEXT_SETTINGS)
def cli():
    # Initialize the CLI group
    pass

cli.add_command(joystick)
cli.add_command(cmd=dds, name="dds")

if __name__ == "__main__":
    cli()
