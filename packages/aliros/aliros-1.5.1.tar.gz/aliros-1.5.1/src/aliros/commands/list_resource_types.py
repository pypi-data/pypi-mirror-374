import click
from aliyunsdkros.request.v20150901.DescribeResourceTypesRequest import DescribeResourceTypesRequest

from aliros.request import send_request


@click.command('list-resource-types')
@click.option('--support-status', help='Status of support.', required=False)
def list_resource_types_command(ctx: click.Context, support_status: str):
    """List available resource types."""

    acs_client = ctx.obj['acs_client']

    request = DescribeResourceTypesRequest()

    if support_status is not None:
        request.set_SupportStatus(support_status)

    send_request(acs_client, request)
