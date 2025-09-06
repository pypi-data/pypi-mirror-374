from projects_organizer import app, __version__
from typer.testing import CliRunner


def test_version():
    runner = CliRunner()
    test_args = ["--version"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 0
    assert result.stdout == f"projects-organizer {__version__}\n"


def test_main_invalid_dir():
    runner = CliRunner(mix_stderr=False)
    test_args = ["-d", "not_exists", "list"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 1
    assert result.stdout == ""
