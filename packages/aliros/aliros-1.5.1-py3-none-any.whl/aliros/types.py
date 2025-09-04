from typing import Any, List

import click


class ListParamType(click.ParamType):
    name = 'list'

    def __init__(self, length=None, item_type=None):
        self.length = length
        self.item_type = item_type

    # pylint: disable=inconsistent-return-statements
    def convert(self, value: Any, param: click.Parameter, ctx: click.Context) -> List[str]:
        if isinstance(value, list):
            return value

        if not isinstance(value, str):
            raise TypeError(type(value))

        try:
            items = [fd.strip() for fd in value.split(',')]

            if self.length is not None and len(items) > self.length:
                raise ValueError(f'Length of list "{value}" is greater than {self.length}.')

            if self.item_type is not None:
                for i, item in enumerate(items):
                    items[i] = self.item_type(item)

            return items

        except ValueError as exc:
            self.fail(str(exc), param, ctx)
