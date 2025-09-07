from abc import ABC, abstractmethod
from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel, PrivateAttr

from mo.core.plugin.models.semantic_version import SemanticVersion
from mo.core.plugin.models.settings import Settings
from mo.core.plugin.models.sys_platform import SysPlatform
from mo.core.plugin.models.validators import validate_id, validate_target


class PluginAuthor(BaseModel):
    """Represents the author of a plugin."""

    name: Optional[str] = None  # Name of the author
    email: Optional[str] = None  # Email of the author


class PluginIcons(BaseModel):
    """Represents icons for a plugin."""

    dark: Optional[str] = None  # Path to the dark mode icon
    light: Optional[str] = None  # Path to the light mode icon


class PluginPublisher(BaseModel):
    """Represents the publisher of a plugin."""

    # Unique identifier for the publisher
    id: Annotated[str, AfterValidator(validate_id)]
    name: str  # Name of the publisher
    url: Optional[str] = None  # URL to the publisher's website


class PluginMetadata(BaseModel):
    """Metadata for a plugin.

    This class contains essential information about a plugin

    Attributes:
        plugin_id (str): Unique identifier for the plugin.
        name (str): Name of the plugin.
        description (str): Description of the plugin.
        version (SemanticVersion): Version of the plugin.
        publisher (PluginPublisher): Publisher of the plugin.
        repository (str): URL to the plugin's repository.
        icon_path (Optional[str] | Optional[PluginIcons]): Path to the plugin's icon or icons.
        locales (Optional[str]): Path to the plugin's locales directory.
        author (Optional[PluginAuthor]): Author of the plugin.
        platform (SysPlatform): Supported platform for the plugin.
        target (str): Target environment for the plugin, must be "api".
    """

    plugin_id: Annotated[str, AfterValidator(validate_id)]
    name: str
    description: str
    version: SemanticVersion
    publisher: PluginPublisher
    repository: str
    icon_path: Optional[str] | Optional[PluginIcons] = None
    locales: Optional[str] = None
    author: Optional[PluginAuthor] = None
    platform: SysPlatform
    target: Annotated[str, AfterValidator(validate_target)]
    _location: Optional[str] = PrivateAttr(
        default=None)  # Location of the plugin files
    _module: Optional[str] = PrivateAttr(
        default=None)  # Module name of the plugin
    # Indicates if the plugin is loaded
    _is_loaded: bool = PrivateAttr(default=False)
    # Error message if the plugin failed to load
    _error: Optional[str] = PrivateAttr(default=None)

    def get_final_id(self) -> str:
        """Generates a final ID for the plugin in the format 'publisher_id.plugin_id'."""
        return f"{self.publisher.id}.{self.plugin_id}"

    def from_final_id(self, final_id: str) -> None:
        """Sets the plugin ID and publisher ID from a final ID string."""
        parts = final_id.split(".")
        if len(parts) != 2:
            raise ValueError(
                "Invalid final ID format. Expected 'publisher_id.plugin_id'.")
        self.publisher.id = parts[0]
        self.plugin_id = parts[1]

    def is_plugin(self, plugin_id: str, publisher_id) -> bool:
        """Checks if the plugin matches the given plugin ID and publisher ID."""
        return self.plugin_id == plugin_id and self.publisher.id == publisher_id

    def is_plugin_from_final_id(self, final_id: str) -> bool:
        """Checks if the plugin matches the given final ID."""
        return self.get_final_id() == final_id


class Plugin(ABC):
    """Base class for plugins in the system.

    This abstract class defines the fundamental interface and lifecycle expected from
    any plugin type within the application. It provides mechanisms for loading,
    unloading, and configuring plugin behavior.

    Plugins that inherit from this class must at minimum implement `load()` and
    `unload()`, and may optionally override `on_configure()` to handle configuration updates.

    Attributes:
        metadata (PluginMetadata): Descriptive metadata for the plugin.
        settings (Settings): Configuration object with parameters used by the plugin.
    """

    metadata: PluginMetadata  # Metadata for the plugin
    settings: Settings = Settings()  # Settings for the plugin
    _module_name: str = "core"  # Module name for the plugin

    @abstractmethod
    def load(self):
        """Load and initialize the plugin.

        This method should perform any required setup to make the plugin operational.
        It is called once when the plugin is loaded by the system.

        Typical tasks include: resource allocation, starting background tasks,
        establishing connections, or validating initial state.
        """
        pass

    @abstractmethod
    def unload(self):
        """Unload and clean up the plugin.

        This method should release any resources acquired during `load()`, stop ongoing
        tasks, and leave the system in a clean state. It is called when the plugin is
        removed.
        """
        pass

    def configure(self, settings: Settings):
        """Configure the plugin with the provided settings.

        This method updates the plugin's internal settings and invokes the
        `on_configure()` hook to let the plugin respond to the new configuration.

        Args:
            settings (Settings): The configuration object for the plugin.
        """
        self.settings = settings
        self.on_configure(settings)

    def on_configure(self, settings: Settings) -> None:
        """Hook for handling dynamic configuration updates.

        Override this method to implement plugin-specific logic when settings are
        updated. Called automatically by `configure()`.

        Args:
            settings (Settings): The updated configuration object.
        """
        pass
