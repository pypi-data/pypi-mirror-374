import pytest
from projects_organizer import app
from typer.testing import CliRunner


def test_show(projects_dir):
    pfilename = "project1"
    runner = CliRunner()
    test_args = ["-d", projects_dir, "show", pytest.projects[pfilename]["title"]]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 0
    assert result.stdout == str(pytest.projects[pfilename]) + "\n"


def test_show_not_found(projects_dir):
    runner = CliRunner(mix_stderr=False)
    test_args = ["-d", projects_dir, "show", "not_found"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 1
    assert result.stdout == ""


def test_show_many_found(projects_dir):
    runner = CliRunner(mix_stderr=False)
    test_args = ["-d", projects_dir, "show", "project"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 1
    assert result.stdout == "Many projects found: Project 1, Project 2, Project 3\n"


def test_show_verbose(projects_dir):
    runner = CliRunner(mix_stderr=False)
    test_args = ["-d", projects_dir, "-v", "show", "project 1"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 0
    lines = result.stdout.strip().split("\n")
    assert "'title': 'project 1'" in lines[len(lines) - 1].lower()
