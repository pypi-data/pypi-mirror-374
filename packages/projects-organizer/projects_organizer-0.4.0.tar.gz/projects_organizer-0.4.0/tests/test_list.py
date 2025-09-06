import pytest
from projects_organizer import app
from typer.testing import CliRunner


def test_list_basic(projects_dir):
    runner = CliRunner()
    test_args = ["-d", projects_dir, "list"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 0
    assert result.stdout == "- Project 1\n- Project 2\n- Project 3\n"


def test_list_basic_verbose(projects_dir):
    runner = CliRunner()
    test_args = ["-d", projects_dir, "-v", "list"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 0
    assert (
        result.stdout
        == f"""Initializing projects from {str(projects_dir)}
Reading file {str(projects_dir / "project1" / "index.md")}
Reading file {str(projects_dir / "project2" / "index.md")}
Reading file {str(projects_dir / "project3" / "index.md")}
- Project 1
- Project 2
- Project 3
"""
    )


def test_list_empty_project(projects_dir_empty_project):
    runner = CliRunner()
    test_args = ["-d", projects_dir_empty_project, "list"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 1
    assert "missing index.md in" in result.stdout.lower()


def test_list_duplicate_project(projects_dir_duplicate_project):
    runner = CliRunner()
    test_args = ["-d", projects_dir_duplicate_project, "list"]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 1
    assert "duplicate project title" in result.stdout.lower()


@pytest.mark.parametrize(
    "filter,expected",
    [
        ("unknown", ""),
        ("not unknown", "- Project 1\n- Project 2\n- Project 3\n"),
        ("archived", "- Project 1\n"),
        ("not archived", "- Project 2\n- Project 3\n"),
        ("'dev' in tags", "- Project 1\n- Project 2\n- Project 3\n"),
        ("'python' in tags", "- Project 1\n- Project 3\n"),
        (
            "datetime.strptime(created_at, '%Y-%m-%d') >= datetime(2024, 1, 1)",
            "- Project 2\n- Project 3\n",
        ),
    ],
)
def test_list_filter(filter, expected, projects_dir):
    runner = CliRunner()
    test_args = ["-d", projects_dir, "list", "-f", filter]
    result = runner.invoke(app, test_args)
    assert result.exit_code == 0
    assert result.stdout == expected


def test_list_filter_invalid(projects_dir):
    runner = CliRunner(mix_stderr=False)
    test_args = ["-d", projects_dir, "list", "-f", "1 + 2"]
    result = runner.invoke(app, test_args)
    assert result.exit_code != 0
    assert len(result.stderr) != 0
