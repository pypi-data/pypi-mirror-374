from aliyunsdkros.request.v20190910.DescribeRegionsRequest import DescribeRegionsRequest

import click

from aliros.request import send_request, dump_response


@click.command('list-regions')
@click.pass_context
def list_regions_command(ctx: click.Context):
    """List available regions."""

    dump_response(send_request(ctx.obj['acs_client'], DescribeRegionsRequest()))
