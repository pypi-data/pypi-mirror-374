import os
from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path

import click
from aliyunsdkcore.client import AcsClient

from aliros import __version__
from aliros.commands import command_group


def print_version(ctx: click.Context, _, value: str):
    if not value or ctx.resilient_parsing:
        return

    click.echo(__version__)
    ctx.exit()


@click.group(commands=command_group)
@click.option('--version', help='Show version information.', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.option('--region', help='Target region to use', required=False, default=os.getenv('ALICLOUD_REGION'))
@click.option('--profile', help='Name of profile to use', required=False, default=os.getenv('ALICLOUD_PROFILE') or 'default')
@click.pass_context
def main(ctx: click.Context, region: str, profile: str):
    """A command-line tool to organize resources by Resource Orchestration Service for Alibaba Cloud."""

    ctx.ensure_object(dict)

    config_file = Path.home() / '.aliros/config'
    creds_file = Path.home() / '.aliros/credentials'

    if creds_file.stat().st_mode & 0o77 != 0:
        ctx.fail(f'Credential file "{creds_file}" is too open.')

    config = ConfigParser()
    config.read(config_file)

    if region is None:
        try:
            region = config.get(profile, 'region')
        except (NoSectionError, NoOptionError):
            region = 'cn-hangzhou'

    try:
        config.read(creds_file)
        access_key_id = config.get(profile, 'alicloud_access_key_id')
        secret_access_key = config.get(profile, 'alicloud_secret_access_key')
    except (NoSectionError, NoOptionError) as exc:
        ctx.fail(f'Load credentials: {exc.message}')
        return
    ctx.obj['acs_client'] = AcsClient(access_key_id, secret_access_key, region)


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
