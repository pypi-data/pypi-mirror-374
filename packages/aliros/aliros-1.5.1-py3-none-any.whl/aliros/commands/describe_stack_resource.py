import click
from aliyunsdkros.request.v20150901.DescribeResourceDetailRequest import DescribeResourceDetailRequest

from aliros.alicloud import find_stack_id
from aliros.request import send_request


@click.command('describe-stack-resource')
@click.option('--stack-name', help='Name of stack.', required=True)
@click.option('--resource-name', help='Name of resource.', required=True)
def describe_stack_resource_command(ctx: click.Context, stack_name: str, resource_name: str):
    """Describe the specified resource in stack."""

    acs_client = ctx.obj['acs_client']
    stack_id = find_stack_id(acs_client, stack_name)

    request = DescribeResourceDetailRequest()

    request.set_StackName(stack_name)
    request.set_StackId(stack_id)
    request.set_ResourceName(resource_name)

    send_request(acs_client, request)
