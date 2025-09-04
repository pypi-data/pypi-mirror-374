import click
from aliyunsdkros.request.v20190910.DeleteStackRequest import DeleteStackRequest

from aliros.request import send_request


@click.command('delete-stack')
@click.option('--stack-id', help='Stack ID', required=True)
@click.pass_context
def delete_stack_command(ctx: click.Context, stack_id: str):
    """Delete the specified stack."""

    acs_client = ctx.obj['acs_client']

    request = DeleteStackRequest()
    request.set_StackId(stack_id)

    send_request(acs_client, request)
