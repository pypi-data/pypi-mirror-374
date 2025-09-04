import click
from aliyunsdkros.request.v20150901.DescribeResourceTypeDetailRequest import DescribeResourceTypeDetailRequest

from aliros.request import send_request


@click.command('describe-resource-type')
@click.option('--type-name', help='Name of stack.', required=True)
def describe_resource_type_command(ctx: click.Context, type_name: str):
    """Describe resource type."""

    acs_client = ctx.obj['acs_client']

    request = DescribeResourceTypeDetailRequest()
    request.set_TypeName(type_name)

    send_request(acs_client, request)
