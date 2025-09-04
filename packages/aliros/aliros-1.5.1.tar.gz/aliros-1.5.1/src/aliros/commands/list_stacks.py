from typing import List, Optional

import click
from aliyunsdkros.request.v20190910.ListStacksRequest import ListStacksRequest

from aliros.request import send_request, dump_response
from aliros.types import ListParamType


@click.command('list-stacks')
@click.option('--stack-names', help='Names of stack.', type=ListParamType(length=5, item_type=str), required=False)
@click.option('--status', help='Status of stack.', type=ListParamType(length=5, item_type=str), required=False)
@click.option('--page-number', help='Number of page.', type=int, default=1, required=False)
@click.option('--page-size', help='Size of pages.', type=int, default=10, required=False)
@click.pass_context
def list_stacks_command(ctx: click.Context, stack_names: Optional[List[str]], status: Optional[List[str]], page_number: int, page_size: int):
    """List stacks."""

    acs_client = ctx.obj['acs_client']

    request = ListStacksRequest()

    if stack_names is not None:
        request.set_StackName(stack_names)

    if status is not None:
        request.set_Status(status)

    request.set_PageNumber(page_number)
    request.set_PageSize(page_size)

    dump_response(send_request(acs_client, request))
