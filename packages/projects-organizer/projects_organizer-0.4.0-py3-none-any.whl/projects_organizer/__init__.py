from pathlib import Path
from typing import TypedDict, Any, cast
from typing_extensions import Annotated
from types import CodeType
from datetime import datetime
import ast
import typer
from rich.console import Console
import frontmatter
import jsonschema
from jsonschema.exceptions import ValidationError, SchemaError
import yaml

__version__ = "0.4.0"


class State(TypedDict):
    verbose: bool
    base_dir: Path


state: State = {
    "verbose": False,
    "base_dir": Path("."),
}


class Project(TypedDict):
    file: Path
    metadata: dict[str, Any]  # pyright: ignore[reportExplicitAny]
    content: str


projects: dict[str, Project] = {}

app = typer.Typer(pretty_exceptions_enable=False)
err_console = Console(stderr=True)

error_code = 1
errors: list[str] = []


def log_error(msg: str):
    errors.append(msg)


MD_FILE_DEFAULT = "index.md"


def init():
    if state["verbose"]:
        print(f"Initializing projects from {state['base_dir']}")
    md_files: list[Path] = []
    for file in state["base_dir"].glob("*"):
        if file.is_dir():
            full_path = file.resolve() / MD_FILE_DEFAULT
            if not full_path.exists() or not full_path.is_file():
                log_error(f"Missing {MD_FILE_DEFAULT} in {file}")
                continue
            md_files.append(full_path)

    if len(errors) != 0:
        return False

    md_files = sorted(md_files)

    projects.clear()
    for file in md_files:
        if state["verbose"]:
            print(f"Reading file {file}")
        with open(file, "r") as f:
            metadata, content = frontmatter.parse(f.read())
            title = cast(str, metadata["title"])
            if title in projects:
                log_error(
                    f"Duplicate project title: {title} in {projects[title]['file']} and {file}"
                )
                continue
            projects[title] = {
                "file": file,
                "metadata": metadata,
                "content": content,
            }

    if len(errors) != 0:
        return False

    return True


def parse_filter(filter: str | None) -> tuple[CodeType, set[str]] | tuple[None, None]:
    if filter is None:
        return None, None

    try:
        parsed = ast.parse(filter, mode="eval")
    except SyntaxError as e:
        log_error(f"Invalid filter: {e}")
        raise ValueError("Invalid filter")

    if (
        not isinstance(parsed.body, ast.BoolOp)
        and not isinstance(parsed.body, ast.UnaryOp)
        and not isinstance(parsed.body, ast.Name)
    ):
        if not isinstance(parsed.body, ast.Compare):
            log_error(f"Invalid filter: {filter}")
            raise ValueError("Invalid filter")

        final = ast.BoolOp(op=ast.And(), values=[parsed.body, ast.Constant(value=True)])
        parsed.body = ast.copy_location(final, parsed.body)
        parsed = ast.fix_missing_locations(parsed)

    compiled = compile(parsed, filename="<ast>", mode="eval")

    variables: set[str] = set()
    for node in ast.walk(parsed):
        if isinstance(node, ast.Name):
            variables.add(node.id)

    return compiled, variables


@app.command("list")
def list_projects(
    filter: Annotated[
        str | None, typer.Option("--filter", "-f", help="Filter by element")
    ] = None,
):
    try:
        compiled, variables = parse_filter(filter)
    except Exception:
        return False

    for p in projects.values():
        if compiled is not None and variables is not None:
            context: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]
            for v in variables:
                if v == "datetime":  # import datetime if used
                    context[v] = datetime
                    continue
                if v not in p["metadata"]:
                    context[v] = ""
                else:
                    context[v] = p["metadata"][v]
            result = cast(bool, eval(compiled, None, context))
            if not result:
                continue

        print(f"- {p['metadata']['title']}")


@app.command()
def show(name: str):
    selected: list[str] = []
    for p in projects.values():
        title = cast(str, p["metadata"]["title"])
        if name.lower() in title.lower():
            selected.append(title)

    if len(selected) == 0:
        log_error(f"Project {name} not found.")

    found = None
    for s in selected:
        if name.lower() == s.lower():
            found = s

    if len(selected) > 1:
        if found is None:
            print(f"Many projects found: {', '.join([p for p in selected])}")
            return False
    elif len(selected) == 1:
        found = selected[0]
    else:
        return False

    if state["verbose"]:
        print(f"Project found: {projects[found]['file']}")
    print(projects[found]["metadata"])


@app.command()
def validate(
    schema: Path,
    stop_on_error: Annotated[
        bool, typer.Option("--stop-on-error", "-s", help="Stop on first error")
    ] = False,
):
    with open(schema, "r") as f:
        sc = yaml.safe_load(f.read())  # pyright: ignore[reportAny]

    invalid: dict[str, str] = {}
    for p in projects.values():
        try:
            jsonschema.validate(p["metadata"], sc)  # pyright: ignore[reportAny]
        except ValidationError as e:
            title = cast(str, p["metadata"]["title"])
            invalid[title] = e.message
        except SchemaError as e:
            log_error(f"Invalid schema: {e}")
            return False

    if len(invalid) != 0:
        if stop_on_error:
            title, error = next(iter(invalid.items()))
            print(f"error for project {title}")
            print(error)
        else:
            for title, error in invalid.items():
                print(f"- {title}: {error}")
        return False

    if len(errors) != 0:
        return False

    print("All projects are valid.")


def version_callback(value: bool):
    if value:
        print(f"projects-organizer {__version__}")
        raise typer.Exit()


def result_cb(
    executed_command_result: Any,  # pyright: ignore[reportAny, reportExplicitAny]
    verbose: bool,  # pyright: ignore[reportUnusedParameter]
    base_dir: Path,  # pyright: ignore[reportUnusedParameter]
    version: bool,  # pyright: ignore[reportUnusedParameter]
):
    projects.clear()
    if len(errors) != 0:
        for e in errors:
            err_console.print(f"[red]error[/red]: {e}")
        errors.clear()
        raise typer.Exit(code=error_code)

    if executed_command_result is not None and executed_command_result is not True:
        raise typer.Exit(code=1)


@app.callback(result_callback=result_cb)
def main_options(
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = state["verbose"],
    base_dir: Annotated[Path, typer.Option("--base_dir", "-d")] = state["base_dir"],
    version: Annotated[  # pyright: ignore[reportUnusedParameter]
        bool | None, typer.Option("--version", callback=version_callback)
    ] = None,
):
    state["verbose"] = verbose
    state["base_dir"] = base_dir

    if not state["base_dir"].exists() and not state["base_dir"].is_dir():
        log_error(
            f"Base directory {state['base_dir']} does not exist or is not a directory."
        )
        return False

    return init()


if __name__ == "__main__":
    app()  # pragma: no cover
