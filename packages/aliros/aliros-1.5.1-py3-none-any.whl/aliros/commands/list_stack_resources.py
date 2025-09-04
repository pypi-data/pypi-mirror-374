import click
from aliyunsdkros.request.v20150901.DescribeResourcesRequest import DescribeResourcesRequest

from aliros.alicloud import find_stack_id
from aliros.request import send_request


@click.command('list-stack-resources')
@click.option('--stack-name', help='Name of stack.', required=True)
def list_stack_resources_command(ctx: click.Context, stack_name: str):
    """List resources of the specified stack."""

    acs_client = ctx.obj['acs_client']

    stack_id = find_stack_id(acs_client, stack_name)

    request = DescribeResourcesRequest()

    request.set_StackName(stack_name)
    request.set_StackId(stack_id)
    send_request(acs_client, request)
