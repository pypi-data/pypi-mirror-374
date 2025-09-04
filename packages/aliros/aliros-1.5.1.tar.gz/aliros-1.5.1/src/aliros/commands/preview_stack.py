import json

import click
from aliyunsdkros.request.v20150901.PreviewStackRequest import PreviewStackRequest

from aliros.request import send_request
from aliros.template import YamlTemplate


@click.command('preview-stack')
@click.option('--stack-name', help='Name of stack.', required=True)
@click.option('--template-file', help='Path of template file.', required=True, type=click.Path(exists=True, dir_okay=False))
@click.option('--parameters-file', help='URL of parameters file.', required=False, type=click.Path(exists=True, dir_okay=False))
@click.option('--timeout-mins', help='Minutes to timeout.', type=int, default=60)
@click.option('--disable-rollback', help='Disable rollback if failed.', required=False, is_flag=True, default=False)
def preview_stack_command(ctx: click.Context, stack_name: str, template_file: str, parameters_file: str, timeout_mins: int, disable_rollback: bool):
    """Preview of creating stack."""

    acs_client = ctx.obj['acs_client']

    template = YamlTemplate()
    template.load(template_file)

    body = {
        'Name': stack_name,
        'Template': json.dumps(template.content),
        'TimeoutMins': timeout_mins,
        'DisableRollback': disable_rollback
    }

    if parameters_file is not None:
        parameters = YamlTemplate()
        parameters.load(parameters_file)
        body['Parameters'] = parameters.content

    request = PreviewStackRequest()
    request.set_content(json.dumps(body))
    request.set_content_type('application/json')

    send_request(acs_client, request)
