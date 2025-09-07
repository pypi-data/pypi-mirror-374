import json
from typing import Any, Optional


class Settings:
    """A class to manage settings for a plugin.
    It allows setting, updating, retrieving, and saving settings in JSON format.
    """

    _settings: dict[str, Any] = {}  # Default empty settings dictionary

    def __init__(self, settings: Optional[dict[str, Any]] = None):
        """Initializes the Settings instance with an optional dictionary of settings.
        Args:
            settings (Optional[dict[str, Any]]): A dictionary of initial settings. Defaults to None.
        """
        self._settings = settings if settings is not None else {}

    def set_settings(self, settings: dict[str, Any]):
        """Sets the settings to the provided dictionary.
        Args:
            settings (dict[str, Any]): A dictionary of settings to set.
        """
        self._settings = settings

    def update_settings(self, settings: dict[str, Any]):
        """Updates the current settings with the provided dictionary.
        Args:
            settings (dict[str, Any]): A dictionary of settings to update.
        """
        self._settings.update(settings)

    def get_settings(self) -> dict[str, Any]:
        """Returns the current settings as a dictionary.
        Returns:
            dict[str, Any]: The current settings.
        """
        return self._settings

    def get_setting(self, key: str) -> Optional[Any]:
        """Retrieves a specific setting by its key.
        Args:
            key (str): The key of the setting to retrieve.
        Returns:
            Optional[Any]: The value of the setting if it exists, otherwise None.
        """
        return self._settings.get(key, None)

    def has_setting(self, key: str) -> bool:
        """Checks if a specific setting exists by its key.
        Args:
            key (str): The key of the setting to check.
        Returns:
            bool: True if the setting exists, otherwise False.
        """
        return key in self._settings

    def save_json(self, file_path: str):
        """Saves the current settings to a JSON file.
        Args:
            file_path (str): The path to the JSON file where settings will be saved.
        """
        with open(file_path, "w") as f:
            json.dump(self._settings, f)

    def load_json(self, file_path: str):
        """Loads settings from a JSON file and updates the current settings.
        Args:
            file_path (str): The path to the JSON file from which settings will be loaded.
        """
        with open(file_path, "r") as f:
            self._settings = dict(json.load(f))

    def __repr__(self) -> str:
        """Returns a string representation of the Settings instance."""
        return f"Settings({self._settings})"

    def __str__(self) -> str:
        """Returns a JSON string representation of the current settings."""
        return json.dumps(self._settings, indent=4, ensure_ascii=False)

    def __getitem__(self, key: str) -> Any:
        """Retrieves a setting by its key.
        Args:
            key (str): The key of the setting to retrieve.
        Returns:
            Any: The value of the setting.
        Raises:
            KeyError: If the key does not exist in the settings.
        """
        return self._settings[key]

    def __setitem__(self, key: str, value: Any):
        """Sets a specific setting by its key.
        Args:
            key (str): The key of the setting to set.
            value (Any): The value to set for the specified key.
        """
        self._settings[key] = value

    def __delitem__(self, key: str):
        """Deletes a specific setting by its key.
        Args:
            key (str): The key of the setting to delete.
        Raises:
            KeyError: If the key does not exist in the settings.
        """
        if key in self._settings:
            del self._settings[key]
        else:
            raise KeyError(f"Key '{key}' not found in settings.")

    def __contains__(self, key: str) -> bool:
        """Checks if a specific setting exists by its key.
        Args:
            key (str): The key of the setting to check.
        Returns:
            bool: True if the setting exists, otherwise False.
        """
        return key in self._settings

    def __len__(self) -> int:
        """Returns the number of settings in the current settings dictionary.
        Returns:
            int: The number of settings.
        """
        return len(self._settings)

    def __iter__(self):
        """Returns an iterator over the settings items.
        Returns:
            Iterator[tuple[str, Any]]: An iterator over the settings items as (key, value) pairs.
        """
        return iter(self._settings.items())
