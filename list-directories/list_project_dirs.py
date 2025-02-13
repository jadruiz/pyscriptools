import os
import json
import argparse
from rich.tree import Tree
from rich.console import Console

# Default exclusions file path (same directory as script)
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "exclusions.json")


def load_exclusions(config_file):
    """
    Loads exclusion lists from a JSON configuration file.

    Args:
        config_file (str): Path to the exclusions.json file.

    Returns:
        tuple: A set of excluded directories and a set of excluded files.
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            return set(config.get("exclude_dirs", [])), set(config.get("exclude_files", []))
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"⚠️ Warning: '{config_file}' not found or has an invalid format.")
        return set(), set()


def get_directory():
    """
    Asks the user to input a directory to scan.

    Returns:
        str: The validated directory path.
    """
    while True:
        dir_path = input("🔹 Enter the directory to scan (or press Enter to use the current directory): ").strip()

        if not dir_path:
            dir_path = os.getcwd()  # Use current directory if nothing is entered
            print(f"✅ Using current directory: {dir_path}")
            return dir_path
        elif os.path.exists(dir_path) and os.path.isdir(dir_path):
            return dir_path
        else:
            print("❌ Invalid directory. Please enter a valid path.")


def build_tree(base_dir, exclude_dirs, exclude_files, tree=None):
    """
    Recursively builds a clean directory tree of the project, excluding specified directories and files.

    Args:
        base_dir (str): The root directory to scan.
        exclude_dirs (set): Set of directories to exclude.
        exclude_files (set): Set of files to exclude.
        tree (Tree, optional): The Rich Tree object to append nodes to.

    Returns:
        Tree: A formatted directory tree structure.
    """
    if tree is None:
        tree = Tree(f"[bold cyan]{base_dir}/[/bold cyan]")  # Root node of the tree

    try:
        entries = sorted(os.listdir(base_dir))  # Sort for better readability
        for entry in entries:
            full_path = os.path.join(base_dir, entry)

            if os.path.isdir(full_path) and entry not in exclude_dirs:
                sub_tree = tree.add(f"[bold blue]📂 {entry}/[/bold blue]")
                build_tree(full_path, exclude_dirs, exclude_files, sub_tree)  # Recursive call

            elif os.path.isfile(full_path) and entry not in exclude_files:
                tree.add(f"📄 {entry}")

    except PermissionError:
        tree.add(f"⚠️ [red]Permission denied: {base_dir}[/red]")

    return tree


if __name__ == "__main__":
    """
    Main execution block.

    - Parses arguments for custom exclusion file.
    - Asks the user for a directory to scan.
    - Loads the directory tree from the selected path.
    - Prints the tree in a structured format using the `rich` library.
    """

    # Argument parser setup
    parser = argparse.ArgumentParser(description="Recursively list project directories while respecting exclusions.")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_FILE, help="Path to the exclusions.json file")
    args = parser.parse_args()

    # Load exclusions
    EXCLUDE_DIRS, EXCLUDE_FILES = load_exclusions(args.config)

    # Get project directory
    console = Console()
    project_dir = get_directory()

    # Print recursive directory tree
    console.print(build_tree(project_dir, EXCLUDE_DIRS, EXCLUDE_FILES), justify="left")
