#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "typer>=0.12.0",
#     "rich>=13.7.0",
#     "pathlib2>=2.3.7"
# ]
# ///
"""
IDE Rules Manager - Copy rules files from rules/ folder to Windsurf or Cursor directories

Usage:
    ./main.py copy --ide windsurf --target /path/to/project
    ./main.py copy --ide cursor --target /path/to/project
    ./main.py copy --ide windsurf  # copies to current directory
"""

import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="ide-rules-manager",
    help="Manage IDE rules files for Windsurf and Cursor",
    add_completion=False,
)
console = Console()


def get_rules_files(source_dir: Path) -> list[Path]:
    """Get all rules files from the rules/ subdirectory."""
    rules_dir = source_dir / "rules"
    if not rules_dir.exists():
        return []
    
    rules_files = []
    for pattern in ["*.md", "*.mdc", "*.txt", "*.json"]:
        rules_files.extend(rules_dir.glob(pattern))
    return rules_files


def transform_rule_filename(filename: str, ide: str) -> str:
    """
    Transform rule filename based on IDE type.
    
    For Windsurf: .mdc -> .md
    For Cursor: .md -> .mdc
    """
    if ide == "windsurf" and filename.endswith(".mdc"):
        return filename[:-4] + ".md"
    elif ide == "cursor" and filename.endswith(".md"):
        return filename[:-3] + ".mdc"
    return filename


def copy_rules_to_target(
    rules_files: list[Path],
    target_dir: Path,
    ide: str,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[int, int]:
    """
    Copy rules files to the target IDE rules directory.

    Args:
        rules_files: List of rule files to copy
        target_dir: Target project directory
        ide: IDE type ("windsurf" or "cursor")
        dry_run: If True, only show what would be copied

    Returns:
        Tuple of (files_copied, files_skipped)
    """
    rules_dir = target_dir / f".{ide}" / "rules"
    files_copied = 0
    files_skipped = 0

    if dry_run:
        console.print(f"[blue]Dry run - would create directory: {rules_dir}[/blue]")
    else:
        rules_dir.mkdir(parents=True, exist_ok=True)

    for source_file in rules_files:
        # Transform filename based on IDE type
        target_name = transform_rule_filename(source_file.name, ide)
        target_file = rules_dir / target_name

        target_exists = target_file.exists()
        if target_exists and not force:
            console.print(f"[yellow]Skipping {source_file.name} -> {target_name} (already exists)[/yellow]")
            files_skipped += 1
            continue

        if dry_run:
            if target_exists and force:
                console.print(f"[green]Would overwrite {source_file.name} -> {target_file}[/green]")
            else:
                console.print(f"[green]Would copy {source_file.name} -> {target_file}[/green]")
        else:
            try:
                shutil.copy2(source_file, target_file)
                if target_exists and force:
                    console.print(f"[green]Overwrote {source_file.name} -> {target_file}[/green]")
                elif target_name != source_file.name:
                    console.print(f"[green]Copied {source_file.name} -> {target_name}[/green]")
                else:
                    console.print(f"[green]Copied {source_file.name} -> {target_file}[/green]")
            except Exception as e:
                console.print(f"[red]Failed to copy {source_file.name}: {e}[/red]")
                continue

        files_copied += 1

    return files_copied, files_skipped


@app.command()
def copy(
    ide: Annotated[
        str,
        typer.Option(
            "--ide",
            "-i",
            help="IDE type to copy rules for",
            case_sensitive=False
        )
    ] = "windsurf",
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            "-t",
            help="Target project directory (defaults to current directory)",
            exists=True,
            file_okay=False,
            dir_okay=True,
        )
    ] = None,
    source: Annotated[
        Path | None,
        typer.Option(
            "--source",
            "-s",
            help="Source directory containing rules/ folder (defaults to current directory)",
            exists=True,
            file_okay=False,
            dir_okay=True,
        )
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-d",
            help="Show what would be copied without actually copying"
        )
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing files"
        )
    ] = False,
) -> None:
    """
    Copy rules files from rules/ folder to the specified IDE's rules directory.

    Examples:
        uv run main.py copy --ide windsurf --target /path/to/project
        uv run main.py copy --ide cursor
        uv run main.py copy --dry-run --ide windsurf
    """
    # Validate IDE choice
    if ide.lower() not in ["windsurf", "cursor"]:
        console.print(f"[red]Error: Invalid IDE '{ide}'. Must be 'windsurf' or 'cursor'[/red]")
        raise typer.Exit(1)

    # Set default directories
    current_dir = Path.cwd()
    target_dir = target or current_dir
    source_dir = source or current_dir

    console.print(Panel.fit(
        f"[bold blue]IDE Rules Manager[/bold blue]\n\n"
        f"IDE: {ide.title()}\n"
        f"Source: {source_dir}\n"
        f"Target: {target_dir}\n"
        f"Mode: {'Dry Run' if dry_run else ('Copy (force)' if force else 'Copy')}"
    ))

    # Get rules files from rules/ subdirectory
    rules_files = get_rules_files(source_dir)
    if not rules_files:
        console.print(f"[yellow]No rules files found in {source_dir}/rules/[/yellow]")
        return

    console.print(f"[blue]Found {len(rules_files)} rules file(s):[/blue]")
    for file in rules_files:
        console.print(f"  • {file.name}")
    console.print()

    # Copy files
    files_copied, files_skipped = copy_rules_to_target(
        rules_files, target_dir, ide.lower(), dry_run, force
    )

    # Summary
    if dry_run:
        console.print(f"\n[blue]Dry run complete - would copy {files_copied} file(s)[/blue]")
    else:
        console.print(f"\n[green]Successfully copied {files_copied} file(s)[/green]")
        if files_skipped > 0:
            console.print(f"[yellow]Skipped {files_skipped} existing file(s)[/yellow]")


@app.command()
def list_ide_rules(
    ide: Annotated[
        str,
        typer.Option(
            "--ide",
            "-i",
            help="IDE type to list rules for",
            case_sensitive=False
        )
    ] = "windsurf",
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            "-t",
            help="Target project directory",
            exists=True,
            file_okay=False,
            dir_okay=True,
        )
    ] = None,
) -> None:
    """
    List existing rules files in the IDE's rules directory.

    Examples:
        uv run main.py list --ide windsurf
        uv run main.py list --ide cursor --target /path/to/project
    """
    if ide.lower() not in ["windsurf", "cursor"]:
        console.print(f"[red]Error: Invalid IDE '{ide}'. Must be 'windsurf' or 'cursor'[/red]")
        raise typer.Exit(1)

    target_dir = target or Path.cwd()
    rules_dir = target_dir / f".{ide}" / "rules"

    if not rules_dir.exists():
        console.print(f"[yellow]Rules directory does not exist: {rules_dir}[/yellow]")
        return

    rules_files = list(rules_dir.glob("*"))
    if not rules_files:
        console.print(f"[yellow]No rules files found in {rules_dir}[/yellow]")
        return

    console.print(f"[blue]Rules files in {rules_dir}:[/blue]")
    for file in sorted(rules_files):
        size = file.stat().st_size
        console.print(f"  • {file.name} ({size} bytes)")


@app.command()
def clean(
    ide: Annotated[
        str,
        typer.Option(
            "--ide",
            "-i",
            help="IDE type to clean rules for",
            case_sensitive=False
        )
    ] = "windsurf",
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            "-t",
            help="Target project directory",
            exists=True,
            file_okay=False,
            dir_okay=True,
        )
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-d",
            help="Show what would be removed without actually removing"
        )
    ] = False,
) -> None:
    """
    Remove all rules files from the IDE's rules directory.

    Examples:
        uv run main.py clean --ide windsurf
        uv run main.py clean --ide cursor --dry-run
    """
    if ide.lower() not in ["windsurf", "cursor"]:
        console.print(f"[red]Error: Invalid IDE '{ide}'. Must be 'windsurf' or 'cursor'[/red]")
        raise typer.Exit(1)

    target_dir = target or Path.cwd()
    rules_dir = target_dir / f".{ide}" / "rules"

    if not rules_dir.exists():
        console.print(f"[yellow]Rules directory does not exist: {rules_dir}[/yellow]")
        return

    rules_files = list(rules_dir.glob("*"))
    if not rules_files:
        console.print(f"[yellow]No rules files to clean in {rules_dir}[/yellow]")
        return

    console.print(f"[red]Cleaning {len(rules_files)} rules file(s) from {rules_dir}:[/red]")
    for file in rules_files:
        if dry_run:
            console.print(f"  • Would remove {file.name}")
        else:
            try:
                file.unlink()
                console.print(f"  • Removed {file.name}")
            except Exception as e:
                console.print(f"  • [red]Failed to remove {file.name}: {e}[/red]")

    if not dry_run and not list(rules_dir.glob("*")):
        try:
            rules_dir.rmdir()
            console.print(f"[blue]Removed empty rules directory: {rules_dir}[/blue]")
        except Exception:
            pass  # Directory not empty or other error, ignore


if __name__ == "__main__":
    app()
