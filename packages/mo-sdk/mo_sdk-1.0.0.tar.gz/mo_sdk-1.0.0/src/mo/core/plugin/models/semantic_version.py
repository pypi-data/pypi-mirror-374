from pydantic import BaseModel


class SemanticVersion(BaseModel):
    """Represents a semantic version in the format major.minor.patch."""

    major: int
    minor: int
    patch: int

    def __str__(self):
        """Returns the version as a string in the format major.minor.patch."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @staticmethod
    def from_string(version_str: str):
        """Creates a SemanticVersion instance from a version string.
        The version string should be in the format 'major.minor.patch'.
        Raises ValueError if the version string is invalid.
        """
        parts = version_str.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version string: {version_str}")
        version = {
            "major": int(parts[0]),
            "minor": int(parts[1]),
            "patch": int(parts[2]),
        }
        return SemanticVersion(**version)
