import click
from aliyunsdkros.request.v20150901.AbandonStackRequest import AbandonStackRequest

from aliros.alicloud import find_stack_id
from aliros.request import send_request


@click.command('abandon-stack')
@click.option('--stack-name', help='Name of stack.', required=True)
def abandon_stack_command(ctx: click.Context, stack_name: str):
    """Abandon the specified stack."""

    acs_client = ctx.obj['acs_client']

    request = AbandonStackRequest()

    request.set_StackName(stack_name)
    request.set_StackId(find_stack_id(acs_client, stack_name))

    send_request(acs_client, request)
