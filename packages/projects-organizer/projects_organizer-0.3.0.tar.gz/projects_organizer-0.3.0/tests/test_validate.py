from projects_organizer import app
from typer.testing import CliRunner


def test_validate(projects_dir, schema_file):
    runner = CliRunner()
    test_args = ["-d", str(projects_dir), "validate", str(schema_file)]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 0
    assert result.stdout == "All projects are valid.\n"


def test_validate_missing_tag(projects_dir, schema_file_missing_tag):
    runner = CliRunner()
    test_args = ["-d", str(projects_dir), "validate", str(schema_file_missing_tag)]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 1
    assert result.stdout != "All projects are valid.\n"
    assert len(result.stdout.strip().split("\n")) == 2


def test_validate_missing_tag_stop(projects_dir, schema_file_missing_tag):
    runner = CliRunner()
    test_args = [
        "-d",
        str(projects_dir),
        "validate",
        str(schema_file_missing_tag),
        "-s",
    ]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 1
    assert result.stdout.startswith("error for project Project 1\n")


def test_validate_invalid(projects_dir, schema_file_invalid):
    runner = CliRunner()
    test_args = ["-d", str(projects_dir), "validate", str(schema_file_invalid)]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 1
    assert "invalid schema" in result.stdout.lower()
