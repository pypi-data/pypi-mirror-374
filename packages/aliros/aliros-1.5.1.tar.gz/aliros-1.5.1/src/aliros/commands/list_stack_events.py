import click
from aliyunsdkros.request.v20150901.DescribeEventsRequest import DescribeEventsRequest

from aliros.alicloud import find_stack_id
from aliros.request import send_request


@click.command('list-stack-events')
@click.option('--stack-name', help='Name of stack.', required=True)
@click.option('--resource-status', help='Status of resource.', required=False)
@click.option('--resource-name', help='Name of resource.', required=False)
@click.option('--resource-type', help='Type of resource.', type=int, default=1, required=False)
@click.option('--page-number', help='Number of page.', type=int, default=1, required=False)
@click.option('--page-size', help='Size of pages.', type=int, default=10, required=False)
def list_stack_events_command(ctx: click.Context, stack_name: str, resource_status: str, resource_name: str, resource_type: int, page_number: int,
                              page_size: int):
    """List events of the specified stack."""

    acs_client = ctx.obj['acs_client']

    stack_id = find_stack_id(acs_client, stack_name)

    request = DescribeEventsRequest()

    request.set_StackName(stack_name)
    request.set_StackId(stack_id)

    if resource_status is not None:
        request.set_ResourceStatus(resource_status)

    if resource_name is not None:
        request.set_ResourceName(resource_status)

    if resource_type is not None:
        request.set_ResourceType(resource_status)

    request.set_PageNumber(page_number)
    request.set_PageSize(page_size)

    send_request(acs_client, request)
