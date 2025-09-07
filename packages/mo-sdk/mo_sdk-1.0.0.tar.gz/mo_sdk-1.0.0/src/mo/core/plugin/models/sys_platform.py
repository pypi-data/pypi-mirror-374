import platform

from pydantic import BaseModel


class SysPlatform(BaseModel):
    """Represents the system platforms supported by a plugin."""

    linux: bool = False
    windows: bool = False
    mac: bool = False

    def is_available(self) -> bool:
        """Checks if the current operating system matches any of the supported platforms."""
        operating_system = platform.system()
        return (
            (self.linux and operating_system == "Linux")
            or (self.windows and operating_system == "Windows")
            or (self.mac and operating_system == "Darwin")  # macOS
        )

    def get_platforms(self) -> list[str]:
        """Returns a list of supported platforms."""
        platforms = []
        if self.linux:
            platforms.append("Linux")
        if self.windows:
            platforms.append("Windows")
        if self.mac:
            platforms.append("macOS")
        return platforms

    def __str__(self) -> str:
        """Returns a string representation of the supported platforms."""
        return self.get_platforms().__str__()
