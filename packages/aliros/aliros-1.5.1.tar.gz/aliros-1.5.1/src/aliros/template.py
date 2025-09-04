import re
from abc import abstractmethod
from typing import Tuple, IO

import yaml


class UrlReader:
    supported_schemes = ['file']

    @staticmethod
    def parse_url(url: str) -> Tuple[str, str]:
        m = re.match(r'^(?P<scheme>[a-z][a-z0-9+\-.]*):(?P<path>.+)', url)

        if m and m.group('scheme') not in UrlReader.supported_schemes:
            raise ValueError(f'URL scheme {m.group("scheme")} not supported.')

        if not m:
            scheme = 'file'
            path = url
        else:
            scheme = m.group('scheme')
            path = m.group('path')

        return scheme, path

    @staticmethod
    def open(url: str) -> IO:
        scheme, path = UrlReader.parse_url(url)

        method = getattr(UrlReader, f'open_{scheme}')

        return method(path)

    @staticmethod
    def open_file(path: str) -> IO:
        return open(path, 'r', encoding='utf-8')


class Template:
    def __init__(self):
        self.content = {}

    def load(self, url: str):
        stream = UrlReader.open(url)
        self.content = self.parse_content(''.join(stream.readlines()))

    @abstractmethod
    def parse_content(self, content):
        ...


class YamlTemplate(Template):

    @staticmethod
    def constructor_ref(loader, node) -> dict:
        value = loader.construct_scalar(node)
        return {'Ref': value}

    @staticmethod
    def constructor_get_att(loader, node) -> dict:
        value = loader.construct_scalar(node).split('.')
        return {'Fn::GetAtt': [value[0], value[1]]}

    @staticmethod
    def constructor_select(loader, node) -> dict:
        value = loader.construct_sequence(node)
        return {'Fn::Select': value}

    @staticmethod
    def constructor_join(loader, node) -> dict:
        value = loader.construct_sequence(node)
        return {'Fn::Join': value}

    @staticmethod
    def add_constructors(loader):
        yaml.add_constructor('!Ref', YamlTemplate.constructor_ref, loader)
        yaml.add_constructor('!GetAtt', YamlTemplate.constructor_get_att, loader)
        yaml.add_constructor('!Select', YamlTemplate.constructor_select, loader)
        yaml.add_constructor('!Join', YamlTemplate.constructor_join, loader)

    def parse_content(self, content: str):
        return yaml.safe_load(content)


YamlTemplate.add_constructors(yaml.SafeLoader)
