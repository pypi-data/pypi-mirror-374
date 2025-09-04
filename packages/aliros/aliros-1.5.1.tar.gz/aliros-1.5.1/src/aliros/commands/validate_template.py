import json

import click
from aliyunsdkros.request.v20150901.ValidateTemplateRequest import ValidateTemplateRequest

from aliros.request import send_request
from aliros.template import YamlTemplate


@click.command('validate-template')
@click.option('--template-file', help='Path of template file.', required=True, type=click.Path(exists=True, dir_okay=False))
def validate_template_command(ctx: click.Context, template_file: str):
    """Validate the specified template."""

    acs_client = ctx.obj['acs_client']

    template = YamlTemplate()
    template.load(template_file)

    body = {
        'Template': json.dumps(template.content)
    }

    request = ValidateTemplateRequest()
    request.set_content(json.dumps(body))
    request.set_content_type('application/json')

    send_request(acs_client, request)
