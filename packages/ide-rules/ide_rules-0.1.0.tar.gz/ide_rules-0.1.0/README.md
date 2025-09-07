# IDE Rules Manager

A tool to manage IDE rules files for Windsurf and Cursor.

## Installation

Install directly from GitHub using uvx:

```bash
uvx run github.com/yourusername/ide-rules --help
```

## Usage

### Copy rules to an IDE

```bash
# Copy to Windsurf in current directory
ide-rules copy --ide windsurf

# Copy to Cursor in a specific directory
ide-rules copy --ide cursor --target /path/to/project

# Dry run to see what would be copied
ide-rules copy --dry-run

# Force overwrite existing files
ide-rules copy --force
```

### List existing rules

```bash
# List Windsurf rules in current directory
ide-rules list-rules --ide windsurf

# List Cursor rules in specific directory
ide-rules list-rules --ide cursor --target /path/to/project
```

### Clean up rules

```bash
# Remove all Windsurf rules (dry run first)
ide-rules clean --ide windsurf --dry-run
ide-rules clean --ide windsurf
```

## Features

- Supports both Windsurf and Cursor IDEs
- Automatically transforms file extensions (.mdc ↔ .md) based on IDE
- Includes a comprehensive set of development rules
- Dry run mode to preview changes
- Force mode to overwrite existing files

## Rules Included

- Domain terminology and naming conventions
- FastAPI deployment patterns
- Makefile development patterns
- Polars data processing best practices
- Prompt engineering patterns
- Python testing with pytest
- Python coding style guidelines
- Script organization patterns
- Typer CLI development
- UV Python package management