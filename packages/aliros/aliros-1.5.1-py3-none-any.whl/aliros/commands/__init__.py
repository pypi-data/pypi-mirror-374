from .abandon_stack import abandon_stack_command
from .create_stack import create_stack_command
from .delete_stack import delete_stack_command
from .describe_resource_type import describe_resource_type_command
from .describe_resource_type_template import describe_resource_type_template_command
from .describe_stack import describe_stack_command
from .describe_stack_resource import describe_stack_resource_command
from .describe_stack_template import describe_stack_template_command
from .list_regions import list_regions_command
from .list_resource_types import list_resource_types_command
from .list_stack_events import list_stack_events_command
from .list_stack_resources import list_stack_resources_command
from .list_stacks import list_stacks_command
from .preview_stack import preview_stack_command
from .update_stack import update_stack_command
from .validate_template import validate_template_command

command_group = [
    abandon_stack_command,
    create_stack_command,
    delete_stack_command,
    describe_resource_type_command,
    describe_resource_type_template_command,
    describe_stack_command,
    describe_stack_resource_command,
    describe_stack_template_command,
    list_regions_command,
    list_resource_types_command,
    list_stack_events_command,
    list_stack_resources_command,
    list_stacks_command,
    preview_stack_command,
    update_stack_command,
    validate_template_command
]
