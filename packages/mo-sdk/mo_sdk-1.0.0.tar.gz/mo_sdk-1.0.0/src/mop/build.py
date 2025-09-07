from pathlib import Path
import os
import sys
import json
import shutil
import subprocess
import tempfile
import argparse
import logging
import traceback

from typing import List, Set, Optional

from mo.core.plugin.metadata_loader import load_plugin_metadata
from mop.utils.logger import setup_logger, Colors
from mop.utils.path import pretty_path

logger = setup_logger()

# Constants
DEFAULT_DIST_DIR = "dist"
DEFAULT_ENTRY_PATH = "."


def load_metadata_file(path: Path) -> dict:
    """
    Loads the metadata.json file from a given directory.

    Args:
        path: Directory Path containing metadata.json.
    Returns:
        Parsed JSON metadata as a dictionary.
    Raises:
        FileNotFoundError: If metadata.json does not exist.
    """
    metadata_path = path / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found at {pretty_path(metadata_path)}")
    with open(metadata_path, "r") as f:
        return json.load(f)


def get_entry_points_path(entry_points: dict) -> List[Path]:
    """
    Converts entry points in module:function format into a list of resolved
    file paths to the Python modules.

    Args:
        entry_points: Dict of entry point names and their module:function strings.
    Returns:
        List of resolved Path objects pointing to the .py files.
    """
    paths = []
    for entry in entry_points.values():
        module_path, _ = entry.split(":")
        module_path = module_path.replace(".", os.sep) + ".py"
        paths.append(Path(module_path).resolve())
    return paths


def generate_requirements_file(entry_points_paths: List[Path], output_path: Path):
    """
    Generates a requirements.txt file using pipreqs based on the given entry points.

    Args:
        entry_points_paths: List of Python file paths to analyze.
        output_path: Path where to save the generated requirements.txt.
    Raises:
        SystemExit: If pipreqs is not installed.
    """
    try:
        subprocess.run(["pipreqs", "--version"],
                       capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error(
            f"{Colors.CYAN.value}pipreqs{Colors.RESET.value} is not installed. Please install it with {Colors.BLUE.value}pip install pipreqs{Colors.RESET.value}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        for entry in entry_points_paths:
            if entry.exists():
                shutil.copy(entry, temp_dir)
            else:
                logger.warning(f"Entry point {pretty_path(entry)} does not exist.")
        cmd = ["pipreqs", "--use-local", "--force",
               "--savepath", str(output_path), temp_dir]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)


def install_dependencies(requirements_file: Path, target: Path):
    """
    Installs Python dependencies from a requirements.txt into the target directory.

    Args:
        requirements_file: Path to requirements.txt.
        target: Directory path to install dependencies into.
    Raises:
        FileNotFoundError: If requirements.txt does not exist.
        CalledProcessError: If pip install fails.
    """
    if not requirements_file.exists():
        raise FileNotFoundError(
            f"Requirements file not found at {pretty_path(requirements_file)}")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file),
                    "--target", str(target), "-qq"], check=True)


def read_ignore_patterns(base_path: Path, use_gitignore: bool, ignore_file: Optional[Path], extra_excludes: List[str]) -> Set[str]:
    """
    Reads ignore patterns from .gitignore, a custom ignore file, and extra excludes.

    Args:
        base_path: Path where .gitignore is located.
        use_gitignore: Whether to read patterns from .gitignore.
        ignore_file: Optional custom ignore file path.
        extra_excludes: Additional ignore patterns from CLI args.
    Returns:
        Set of ignore patterns.
    """
    patterns = set()

    if use_gitignore:
        gitignore = base_path / ".gitignore"
        if gitignore.exists():
            with open(gitignore) as f:
                patterns.update(
                    line.strip() for line in f if line.strip() and not line.startswith("#"))

    if ignore_file and ignore_file.exists():
        with open(ignore_file) as f:
            patterns.update(line.strip()
                            for line in f if line.strip() and not line.startswith("#"))

    if extra_excludes:
        patterns.update(extra_excludes)

    return patterns


def build_plugin(args):
    """
    Main build function to package the plugin based on provided arguments.

    Args:
        args: Parsed CLI arguments with plugin build configuration.

    Steps:
        - Load plugin metadata and validate entry points.
        - Generate or copy requirements.txt.
        - Install dependencies unless skipped.
        - Collect ignore patterns and copy plugin files to a temp directory.
        - Package the plugin into a ZIP file in the output directory.
        - Log useful info about the build progress and final package.
    """
    base_path = Path(args.entry).resolve()
    dist_dir = Path(args.output).resolve()
    dist_dir.mkdir(exist_ok=True)

    metadata_path = base_path / "metadata.json"
    plugin_metadata = load_plugin_metadata(str(metadata_path))
    logger.info(f"Building plugin {Colors.CYAN.value}{plugin_metadata.name}{Colors.RESET.value} "
                f"v{plugin_metadata.version} "
                f"{Colors.GREY.value}[{plugin_metadata.get_final_id()}]{Colors.RESET.value}")
    metadata = load_metadata_file(base_path)
    plugin_id = plugin_metadata.plugin_id

    entry_points = metadata.get("entryPoints", {})
    if not entry_points:
        raise ValueError("No entry points defined in metadata.json")

    entry_paths = get_entry_points_path(entry_points)

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp = Path(temp_dir)
        deps_dir = tmp / "dependencies"
        deps_dir.mkdir()

        req_file = tmp / "requirements.txt"

        if args.requirements:
            logger.info(f"Using custom requirements file: {args.requirements}")
            shutil.copy(Path(args.requirements), req_file)
        else:
            logger.info("Generating requirements.txt from entry points...")
            generate_requirements_file(entry_paths, req_file)

        if not args.skip_deps:
            logger.info("Installing dependencies...")
            install_dependencies(req_file, deps_dir)

        # Prepare ignore patterns for shutil.copytree
        ignore_patterns: Set[str] = set()
        ignore_patterns.add(args.output)
        ignore_patterns.add(DEFAULT_DIST_DIR)
        ignore_patterns.add(".git")
        ignore_patterns.add(".gitignore")

        extra_ignore_patterns = read_ignore_patterns(base_path, not args.no_gitignore, Path(
            args.ignore_file) if args.ignore_file else None, args.exclude)
        ignore_patterns.update(extra_ignore_patterns)
        ignore_fn = shutil.ignore_patterns(
            *ignore_patterns)

        # Debug log excluded files/folders
        if logger.level <= logging.DEBUG:
            logger.debug("Files/folders being excluded:")
            for pattern in sorted(ignore_patterns):
                logger.debug(f"  - {pattern}")
        package_dir = dist_dir / plugin_id

        # Copy plugin files excluding ignored ones
        shutil.copytree(base_path, package_dir,
                        dirs_exist_ok=True, ignore=ignore_fn)

        # Copy requirements.txt and dependencies into package
        shutil.copy(req_file, package_dir / "requirements.txt")
        if not args.skip_deps:
            shutil.copytree(deps_dir, package_dir /
                            "dependencies", dirs_exist_ok=True)

        logger.info("Packaging plugin contents...")

        # Create ZIP archive of the package
        output_zip = dist_dir / f"{plugin_id}-{plugin_metadata.version}.zip"
        shutil.make_archive(str(output_zip).replace(
            ".zip", ""), 'zip', package_dir)
        
        # Clean up temporary package directory
        shutil.rmtree(package_dir)

        # Log final success message with size of zip
        zip_size_mb = output_zip.stat().st_size / (1024 * 1024)
        logger.info(
            f"Plugin {Colors.GREEN.value}built successfully{Colors.RESET.value} at "
            f"{pretty_path(output_zip)} {Colors.GREY.value}({zip_size_mb:.2f} MB){Colors.RESET.value}")


def parse_args():
    """
    Parses command line arguments for the plugin builder.

    Returns:
        Namespace with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Multimodal Observer Plugin (MOP) Builder")

    parser.add_argument("-e", "--entry", default=DEFAULT_ENTRY_PATH,
                        help="Path to plugin root (should contain metadata.json)")
    parser.add_argument("-o", "--output", default=DEFAULT_DIST_DIR,
                        help="Output directory for the build")
    parser.add_argument(
        "--ignore-file", help="Custom ignore file with exclude patterns (like .gitignore)")
    parser.add_argument("--exclude", nargs="*", default=[],
                        help="Extra files/folders to exclude from the package (space-separated)")
    parser.add_argument("--no-gitignore", action="store_true",
                        help="Do not read .gitignore for ignore patterns")
    parser.add_argument("-r", "--requirements", 
                        help="Use a custom requirements.txt file")
    parser.add_argument("--skip-deps", action="store_true",
                        help="Skip dependency installation")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress all output except errors")

    return parser.parse_args()


def main():
    """
    Main entry point: parses arguments, configures logging, and runs build_plugin.
    Handles unexpected exceptions by logging full traceback.
    """
    args = parse_args()

    # Adjust log level based on CLI flags
    if args.quiet:
        logger.setLevel(logging.ERROR)
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    try:
        build_plugin(args)
    except Exception as e:
        logger.error(f"An unexpected error occurred")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
