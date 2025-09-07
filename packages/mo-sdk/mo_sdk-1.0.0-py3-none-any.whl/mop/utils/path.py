from pathlib import Path


def pretty_path(path: Path) -> str:
    """
    Returns a path string relative to the current working directory if possible,
    else returns the absolute path.

    Args:
        path: Path object.
    Returns:
        A string representing a relative or absolute path.
    """
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        # If the path is not relative to the current working directory, return absolute path
        return str(path)
