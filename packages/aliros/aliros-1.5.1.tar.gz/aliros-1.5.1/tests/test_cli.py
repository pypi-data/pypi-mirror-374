from click.testing import CliRunner

from aliros import __version__
from aliros.__cli__ import main


def test_cli_version(cli_runner: CliRunner):
    result = cli_runner.invoke(main, ['--version'])

    assert not result.exception
    assert result.output.strip() == __version__
