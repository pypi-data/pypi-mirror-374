import pytest
import yaml


projects = {
    "project1": {
        "title": "Project 1",
        "created_at": "2023-01-01",
        "archived": True,
        "tags": ["dev", "python"],
    },
    "project2": {
        "title": "Project 2",
        "created_at": "2024-01-01",
        "tags": ["dev", "C++"],
    },
    "project3": {
        "title": "Project 3",
        "created_at": "2025-01-01",
        "tags": ["dev", "python"],
    },
}


schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
        },
        "created_at": {
            "type": "string",
            "format": "date",
        },
        "archived": {
            "type": "boolean",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string", "enum": ["dev", "python", "C++"]},
        },
    },
    "required": ["title"],
    "additionalProperties": False,
}


schema_missing_tag = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
        },
        "created_at": {
            "type": "string",
            "format": "date",
        },
        "archived": {
            "type": "boolean",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string", "enum": ["dev", "C++"]},
        },
    },
    "required": ["title"],
    "additionalProperties": False,
}


schema_invalid = {
    "type": "object",
    "properties": {
        "title": "foo",
        "date": {
            "type": "string",
            "format": "date",
        },
        "archived": {
            "type": "boolean",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string", "enum": ["dev", "C++"]},
        },
    },
    "required": ["title"],
    "additionalProperties": False,
}


def pytest_configure():
    pytest.projects = projects


def create_projects_to_dir(projects, p_dir):
    for name, data in projects.items():
        p_subdir = p_dir / name
        if not p_subdir.exists():
            p_subdir.mkdir()
        with open(p_subdir / "index.md", "w") as f:
            f.write("---\n")
            f.write(
                yaml.dump(data, indent=2, default_flow_style=False, sort_keys=False)
            )
            f.write("---\n")
            f.write("My description")
    return p_dir


@pytest.fixture(scope="session")
def projects_dir(tmp_path_factory):
    return create_projects_to_dir(projects, tmp_path_factory.mktemp("projects_valid"))


@pytest.fixture(scope="session")
def projects_dir_empty_project(tmp_path_factory):
    dir = create_projects_to_dir(
        projects, tmp_path_factory.mktemp("projects_with_empty")
    )
    p_subdir = dir / "project_empty"
    if not p_subdir.exists():
        p_subdir.mkdir()
    return dir


@pytest.fixture(scope="session")
def projects_dir_duplicate_project(tmp_path_factory):
    import copy

    projects_dup = copy.deepcopy(projects)
    projects_dup["project_dup"] = projects_dup["project1"]
    return create_projects_to_dir(
        projects_dup, tmp_path_factory.mktemp("projects_with_dup")
    )


def write_data_to_file(data, filename):
    with open(filename, "w") as f:
        f.write(yaml.dump(data, indent=2, default_flow_style=False, sort_keys=False))
    return filename


@pytest.fixture(scope="session")
def schema_file(projects_dir):
    return write_data_to_file(schema, projects_dir / "schema.yaml")


@pytest.fixture(scope="session")
def schema_file_missing_tag(projects_dir):
    return write_data_to_file(schema_missing_tag, projects_dir / "invalid_schema.yaml")


@pytest.fixture(scope="session")
def schema_file_invalid(projects_dir):
    return write_data_to_file(schema_invalid, projects_dir / "invalid_schema.yaml")
