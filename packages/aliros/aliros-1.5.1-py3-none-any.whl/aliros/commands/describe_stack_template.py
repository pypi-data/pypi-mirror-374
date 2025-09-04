import click
from aliyunsdkros.request.v20150901.DescribeTemplateRequest import DescribeTemplateRequest

from aliros.alicloud import find_stack_id
from aliros.request import send_request


@click.command('describe-stack-template')
@click.option('--stack-name', help='Name of stack.', required=True)
def describe_stack_template_command(ctx: click.Context, stack_name: str):
    """Describe template of the specified stack."""

    acs_client = ctx.obj['acs_client']
    stack_id = find_stack_id(acs_client, stack_name)

    request = DescribeTemplateRequest()

    request.set_StackName(stack_name)
    request.set_StackId(stack_id)

    send_request(acs_client, request)
