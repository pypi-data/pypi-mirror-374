import click
from aliyunsdkros.request.v20150901.DescribeResourceTypeTemplateRequest import DescribeResourceTypeTemplateRequest

from aliros.request import send_request


@click.command('describe-resource-type-template')
@click.option('--type-name', help='Name of resource type.', required=True)
def describe_resource_type_template_command(ctx: click.Context, type_name: str):
    """Describe resource type template."""

    acs_client = ctx.obj['acs_client']

    request = DescribeResourceTypeTemplateRequest()
    request.set_TypeName(type_name)

    send_request(acs_client, request)
