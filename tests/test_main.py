"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner

from awscli_bastion import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0


def test_main_prints_help(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, ["--help"])
    assert "--help" in result.output
    assert result.exit_code == 0


def test_session_token_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, ["session-token"])
    assert result.exit_code == 0


def test_assume_role_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, ["assume-role", "fake-profile"])
    assert result.exit_code == 0


def test_set_default_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, ["set-default", "fake-profile"])
    assert result.exit_code == 0


def test_set_mfa_serial_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, ["set-mfa-serial"])
    assert result.exit_code == 0


def test_show_expiration_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, ["show-expiration"])
    assert result.exit_code == 0


def test_rotate_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, ["rotate"])
    assert result.exit_code == 0


def test_clear_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, ["clear"])
    assert result.exit_code == 0
