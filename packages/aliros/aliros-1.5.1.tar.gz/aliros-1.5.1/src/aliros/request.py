import json
import sys
from dataclasses import dataclass
from typing import Any, IO

from aliyunsdkcore.client import AcsClient, AcsRequest


def send_request(acs_client: AcsClient, request: AcsRequest) -> Any:
    request.set_accept_format('JSON')
    status, _, body = acs_client.get_response(request)

    if 200 <= status < 300:
        return json.loads(body)

    raise AcsError(request.get_action_name(), status, body)


def dump_response(response: Any, output: IO = sys.stdout):
    output.write(json.dumps(response, indent=4, ensure_ascii=False))


@dataclass
class AcsError(RuntimeError):
    action: str
    status: int
    body: str
