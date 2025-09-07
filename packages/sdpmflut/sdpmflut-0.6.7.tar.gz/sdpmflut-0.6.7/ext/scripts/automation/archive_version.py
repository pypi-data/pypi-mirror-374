"""
Script to archive the current version including src/, tests/, docs/, and data/ folders.
Copies the existing directories to ext/archive/versions/ based on the current version.
At minimum, src/ directory must exist. Other directories are included if present.
"""

import os
import sys
import zipfile
import fnmatch
import time
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn


def get_current_version():
    """Get the current version from the __version__.py file."""
    version_file = (
        Path(__file__).parent.parent.parent.parent
        / "src"
        / "sdpmflut"
        / "__version__.py"
    )

    if not version_file.exists():
        print(f"Error: Version file not found at {version_file}")
        sys.exit(1)

    # Import the version module to get the actual values
    import importlib.util

    spec = importlib.util.spec_from_file_location("version_module", version_file)
    if spec is None or spec.loader is None:
        print("Error: Could not load version module")
        sys.exit(1)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)

    return version_module.__version__


def should_exclude_file(file_path, exclude_patterns):
    """Check if a file should be excluded based on patterns."""
    file_str = str(file_path)
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(file_str, pattern) or pattern in file_str:
            return True
    return False


def play_completion_sound():
    """Play a sound notification for archive completion."""
    try:
        # Try to use system bell
        print("\a", end="", flush=True)  # ASCII bell character
    except:
        pass  # Silently ignore if bell doesn't work


def animate_success_banner(version, dest_path, timestamp, file_count, archive_size):
    """Animate the success banner with rich animations."""
    console = Console()

    # Create colorful content with clickable link
    title_text = Text("✅ ARCHIVE SUCCESSFUL ✅", style="bold green")
    title_text.stylize("bold magenta", 0, 1)
    title_text.stylize("bold magenta", -1, 1)

    # Create clickable link to archive location
    archive_link = f"file://{dest_path.parent}"
    link_text = f"[link={archive_link}][bold blue underline]{dest_path.name}[/bold blue underline][/link]"

    content = f"""
[bold green]Version:[/bold green] [bold yellow]{version}[/bold yellow]
[bold green]Files:[/bold green] [bold yellow]{file_count}[/bold yellow]
[bold green]Size:[/bold green] [bold red]{archive_size}[/bold red]
[bold green]Timestamp:[/bold green] [bold blue]{timestamp}[/bold blue]
[bold green]Location:[/bold green] {link_text}
"""

    # Create animated panel
    panel = Panel(
        content.strip(),
        title=title_text,
        border_style="green",
        padding=(1, 3),
        title_align="center",
    )

    # Animate the banner appearance
    with console.status("[bold green]Displaying Info...[/bold green]", spinner="dots"):
        time.sleep(0.5)
        console.clear()
        console.print(panel)
        time.sleep(0.3)

    # Play completion sound
    play_completion_sound()


def print_success_banner(version, dest_path, timestamp, file_count, archive_size):
    """Print a colorful success banner with archive information using rich."""
    animate_success_banner(version, dest_path, timestamp, file_count, archive_size)


def archive_current_version():
    """Archive the current src/, tests/, docs/, and data/ folders based on version."""
    # Get the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent

    # Get current version
    version = get_current_version()
    print(f"Current version: {version}")

    # Generate timestamp prefix for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"v{version}_{timestamp}.zip"

    # Define paths
    source_dirs = ["src", "tests", "docs", "data"]
    source_paths = [project_root / dir_name for dir_name in source_dirs]
    archive_base = project_root / "ext" / "archive" / "versions"
    dest_path = archive_base / archive_name

    # Exclusion patterns
    exclude_patterns = [
        "*.pyc",
        "__pycache__",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
        "Thumbs.db",
        "*.tmp",
        "*.log",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "*.egg-info",
    ]

    # Check if required source directories exist (at least src/ must exist)
    existing_paths = [path for path in source_paths if path.exists()]
    if not (project_root / "src").exists():
        print(f"Error: Required source directory {project_root / 'src'} does not exist")
        sys.exit(1)

    if existing_paths:
        print(f"Found directories to archive: {[path.name for path in existing_paths]}")
    else:
        print("Error: No source directories found to archive")
        sys.exit(1)

    # Create archive directory if it doesn't exist
    archive_base.mkdir(parents=True, exist_ok=True)

    # Check if destination already exists
    if dest_path.exists():
        print(f"Warning: Archive for version {version} already exists at {dest_path}")
        response = input("Overwrite? (y/N): ").lower().strip()
        if response not in ["y", "yes"]:
            print("Archive cancelled.")
            return
        dest_path.unlink()  # Remove the existing zip file

    # Create ZIP archive with progress indicator
    console = Console()
    print(f"Creating ZIP archive {dest_path}...")

    # Count total files first for progress bar
    total_files = 0
    for source_path in existing_paths:
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [
                d
                for d in dirs
                if not should_exclude_file(Path(root) / d, exclude_patterns)
            ]
            for file in files:
                file_path = Path(root) / file
                if not should_exclude_file(file_path, exclude_patterns):
                    total_files += 1

    file_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        console=console,
        refresh_per_second=10,
    ) as progress:
        archive_task = progress.add_task("Creating archive...", total=total_files)

        with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Walk through each source directory and add all files
            for source_path in existing_paths:
                for root, dirs, files in os.walk(source_path):
                    # Filter out excluded directories
                    dirs[:] = [
                        d
                        for d in dirs
                        if not should_exclude_file(Path(root) / d, exclude_patterns)
                    ]

                    for file in files:
                        file_path = Path(root) / file
                        if should_exclude_file(file_path, exclude_patterns):
                            console.print(
                                f"  [dim]Excluded: {file_path.relative_to(project_root)}[/dim]"
                            )
                            continue

                        # Calculate relative path for the ZIP archive
                        relative_path = file_path.relative_to(project_root)
                        zipf.write(file_path, relative_path)

                        file_count += 1
                        progress.update(
                            archive_task,
                            advance=1,
                            description=f"Adding: {relative_path}",
                        )

    # Get archive size
    archive_size = f"{dest_path.stat().st_size / 1024:.1f} KB"

    # Print success banner
    print_success_banner(version, dest_path, timestamp, file_count, archive_size)


if __name__ == "__main__":
    archive_current_version()
