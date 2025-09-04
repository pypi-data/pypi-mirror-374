import json

import click
from aliyunsdkros.request.v20150901.UpdateStackRequest import UpdateStackRequest

from aliros.alicloud import find_stack_id
from aliros.request import send_request
from aliros.template import YamlTemplate


@click.command('update-stack')
@click.option('--stack-name', help='Name of stack.', required=True)
@click.option('--template-file', help='Path of template file.', required=True, type=click.Path(exists=True, dir_okay=False))
@click.option('--timeout-mins', help='Minutes to timeout.', type=int, default=60)
def update_stack_command(ctx: click.Context, stack_name: str, template_file: str, timeout_mins: int):
    """Update the specified stack."""

    acs_client = ctx.obj['acs_client']

    template = YamlTemplate()
    template.load(template_file)

    body = {
        'Template': json.dumps(template.content),
        'TimeoutMins': timeout_mins,
    }

    request = UpdateStackRequest()

    request.set_StackName(stack_name)
    request.set_StackId(find_stack_id(acs_client, request))

    request.set_content(json.dumps(body))
    request.set_content_type('application/json')

    send_request(acs_client, request)
