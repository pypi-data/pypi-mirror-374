import json
import os
from typing import Type, TypeVar

from pydantic import ValidationError

from mo.core.plugin.models.plugin import (
    Plugin,
    PluginAuthor,
    PluginIcons,
    PluginMetadata,
    PluginPublisher,
)
from mo.core.plugin.models.semantic_version import SemanticVersion
from mo.core.plugin.models.sys_platform import SysPlatform


def load_plugin_metadata(path: str) -> PluginMetadata:
    """
    Load plugin metadata from a JSON file.
    Args:
        path (str): The path to the metadata JSON file.
    Returns:
        PluginMetadata: An instance of PluginMetadata containing the loaded data.
    Raises:
        FileNotFoundError: If the metadata file does not exist.
        ValueError: If the metadata file is not in the correct format or contains invalid data.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Metadata file not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        metadata_dict = {
            "plugin_id": data.get("id"),
            "name": data.get("name"),
            "description": data.get("description"),
            "version": SemanticVersion.from_string(data.get("version")),
            "publisher": PluginPublisher(**data.get("publisher")),
            "repository": data.get("repository"),
            "author": PluginAuthor(**data.get("author")) if data.get("author") else None,
            "platform": SysPlatform(**data.get("platform")),
            "target": data.get("target"),
            "locales": data.get("locales")
        }
        icon = data.get("icon")
        if icon and isinstance(icon, dict):
            metadata_dict["icon_path"] = PluginIcons(**icon)
        else:
            metadata_dict["icon_path"] = icon
        try:
            return PluginMetadata(**metadata_dict)
        except ValidationError as e:
            raise ValueError(f"Invalid metadata format: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")


T = TypeVar("T", bound=Plugin)


def load_metadata_json(rel_path: str = ""):
    """
    Load the metadata.json file navigating from the current class directory to the relative path
    Args:
        rel_path (str): The relative path from the current class directory to the metadata.json file.
    Returns:
        A decorator that loads the metadata.json file and attaches it to the Plugin class.
    Raises:
        TypeError: If the class is not a subclass of Plugin.
        RuntimeError: If the base file cannot be found in the stack.
        FileNotFoundError: If the metadata file does not exist at the specified path.
        ValueError: If the metadata file is not in the correct format or contains invalid data.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        if not issubclass(cls, Plugin):
            raise TypeError(f"{cls.__name__} must be a subclass of Plugin")
        import inspect
        import os

        stack = inspect.stack()
        for frame in stack:
            if frame.function == "<module>":
                base_file = frame.filename
                break
        else:
            raise RuntimeError("Could not find the base file in the stack.")

        base_file_dir = os.path.dirname(os.path.abspath(base_file))
        base_plugin_dir = os.path.join(base_file_dir, rel_path)
        base_plugin_dir = os.path.abspath(base_plugin_dir)
        metadata_path = os.path.join(base_plugin_dir, "metadata.json")

        cls.metadata = load_plugin_metadata(metadata_path)
        cls.metadata._module = cls._module_name
        cls.metadata._is_loaded = True
        cls.metadata._location = base_plugin_dir
        return cls

    return decorator
