from aliyunsdkcore.client import AcsClient
from aliyunsdkros.request.v20150901.DescribeStacksRequest import DescribeStacksRequest

from .request import send_request


def find_stack_id(acs_client: AcsClient, stack_name: str):
    request = DescribeStacksRequest()
    request.set_Name(stack_name)

    response = send_request(acs_client=acs_client, request=request)

    if response['TotalCount'] > 1:
        raise RuntimeError(f'Multiple stacks found with name "{stack_name}".')

    if response['TotalCount'] == 0:
        raise RuntimeError(f'Stack with name "{stack_name}" not found.')

    return response['Stacks'][0]['Id']
