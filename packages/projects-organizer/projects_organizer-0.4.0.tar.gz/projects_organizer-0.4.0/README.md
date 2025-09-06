# Projects Organizer

A command-line tool designed to help you organize and document your projects with a consistent structure using Markdown files and YAML frontmatter.

## Features

- **Command-Line Interface**: Easy-to-use CLI tool for managing projects
- **Structured Project Organization**:
  - Each project is contained in its own folder
  - Standardized `index.md` file for project documentation
  - Support for project images and attachments
- **YAML Frontmatter**: Structured metadata for each project
- **Flexible Documentation**: Markdown-based project descriptions

## Installation

You can install Projects Organizer in two ways:

### From PyPI (Recommended)
```bash
pip install projects-organizer
```

### From Release
1. Download the latest wheel file from the [releases page](https://github.com/RomainGiraud/projects-organizer/releases)
2. Install using pip:
```bash
pip install projects_organizer-*-py3-none-any.whl
```

## Usage

Projects Organizer is built with [Typer](https://typer.tiangolo.com/) and provides an intuitive command-line interface. Here are some common commands:

```bash
# Show help
projects-organizer --help

# List all projects
projects-organizer list

# List all projects in the specified directory
projects-organizer -d ../my_projects list

# Filter projects
projects-organizer list -f '"coding" in title'

# Show details of a specific project
projects-organizer show MyFirstProject

# Validate all projects with the following schema
projects-organizer validate schema.yaml
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.
