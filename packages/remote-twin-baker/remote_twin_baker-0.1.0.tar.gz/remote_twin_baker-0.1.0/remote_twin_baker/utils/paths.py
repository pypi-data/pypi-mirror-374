from pathlib import Path


def get_project_root() -> Path:
    """Find the project root by looking for a marker file (README.md)."""
    current_path = Path(__file__).resolve().parent
    while current_path != current_path.parent:  # Stop at filesystem root
        if (current_path / "README.md").exists() and (
            current_path / "LICENSE"
        ).exists():
            return current_path
        current_path = current_path.parent
    raise RuntimeError("Project root not found (missing README.md)")


def to_absolute_path(relative_path: str) -> str:
    """
    Convert a relative path to an absolute path based on project root.

    Args:
        relative_path: Path relative to the project root.

    Returns:
        Absolute path as a string.

    Raises:
        ValueError: If the resolved path escapes the project root.
    """
    project_root = get_project_root()
    abs_path = (project_root / relative_path).resolve()

    # Ensure the path doesn't escape the project root
    if not str(abs_path).startswith(str(project_root)):
        raise ValueError(f"Path '{relative_path}' escapes project root")

    return str(abs_path)
