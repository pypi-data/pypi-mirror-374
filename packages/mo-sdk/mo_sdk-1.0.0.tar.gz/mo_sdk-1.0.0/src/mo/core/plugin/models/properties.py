import copy
from enum import Enum
from typing import Any, Callable, Optional

from pydantic import BaseModel, PrivateAttr

from mo.core.plugin.models.settings import Settings


class PropertyType(Enum):
    """Enumeration for different property types."""

    INT = "int"
    FLOAT = "float"
    TEXT = "text"
    BOOL = "bool"
    PATH = "path"
    SELECT = "select"


# Callback type for modified properties.
modified_callback_type = Callable[
    ["Properties", Settings], Optional[dict[str, "Property"]]
]


class PropertySelectOption(BaseModel):
    """Represents an option for a select property."""

    label: str
    value: str | int | float


class Property(BaseModel):
    """Represents a setting property, which can be of various types."""

    key: str  # Unique identifier for the property
    label: str  # Display label for the property
    required: bool = True  # Indicates if the property is required
    visible: bool = True  # Indicates if the property is visible
    enabled: bool = True  # Indicates if the property is enabled
    default: Optional[Any] = None  # Default value for the property
    # Additional data for the property, such as min/max values or options
    data: dict[str, Any] = {}
    # Type of the property (int, float, text, etc.)
    _type: PropertyType = PrivateAttr()
    _modified_callback: Optional[modified_callback_type] = PrivateAttr(
        default=None
    )  # Callback for when the setting is modified

    def get_dict(self) -> dict[str, Any]:
        """Returns a dictionary representation of the property."""
        return {
            "key": self.key,
            "label": self.label,
            "required": self.required,
            "visible": self.visible,
            "enabled": self.enabled,
            "default": self.default,
            "data": self.data,
            "property_type": self._type.value,
            "reactive": self._modified_callback is not None,
        }


# Validators for each property type to ensure the value is of the correct type.
VALIDATORS = {
    PropertyType.INT: lambda v: isinstance(v, int),
    PropertyType.FLOAT: lambda v: isinstance(v, (float, int)),
    PropertyType.TEXT: lambda v: isinstance(v, str),
    PropertyType.BOOL: lambda v: isinstance(v, bool),
    PropertyType.PATH: lambda v: isinstance(v, str),
    PropertyType.SELECT: lambda v, options: v in [opt.value for opt in options],
}


class Properties:
    """Manages a collection of setting properties for a plugin."""

    _properties: dict[str, Property]

    def __init__(self):
        """Initializes the Properties instance with an empty dictionary for properties."""
        self._properties = {}

    def _add_property(
        self, key: str, label: str, property_type: PropertyType, data: dict[str, Any] = {}
    ):
        """Adds a new property to the collection.
        Args:
            key (str): Unique identifier for the property.
            label (str): Display label for the property.
            property_type (PropertyType): Type of the property (int, float, text, etc.).
            data (dict[str, Any]): Additional data for the property, such as min/max values or options.
        Raises:
            ValueError: If a property with the same key already exists.
        """
        if key in self._properties:
            raise ValueError(f"Property with key '{key}' already exists.")
        self._properties[key] = Property(key=key, label=label, data=data)
        self._properties[key]._type = property_type

    def add_int(
        self,
        key: str,
        label: str,
        min: Optional[int] = None,
        max: Optional[int] = None,
        step: Optional[int] = None,
    ):
        """Adds an integer property to the collection.
        Args:
            key (str): Unique identifier for the property.
            label (str): Display label for the property.
            min (Optional[int]): Minimum value for the property.
            max (Optional[int]): Maximum value for the property.
            step (Optional[int]): Step size for the property.
        """
        data = {}
        if min is not None:
            data["min"] = min
        if max is not None:
            data["max"] = max
        if step is not None:
            data["step"] = step
        self._add_property(key, label, PropertyType.INT, data)

    def add_float(
        self,
        key: str,
        label: str,
        min: Optional[float] = None,
        max: Optional[float] = None,
        step: Optional[float] = None,
    ):
        """Adds a float property to the collection.
        Args:
            key (str): Unique identifier for the property.
            label (str): Display label for the property.
            min (Optional[float]): Minimum value for the property.
            max (Optional[float]): Maximum value for the property.
            step (Optional[float]): Step size for the property.
        """
        data = {}
        if min is not None:
            data["min"] = min
        if max is not None:
            data["max"] = max
        if step is not None:
            data["step"] = step
        self._add_property(key, label, PropertyType.FLOAT, data)

    def add_text(
        self,
        key: str,
        label: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ):
        """Adds a text property to the collection.
        Args:
            key (str): Unique identifier for the property.
            label (str): Display label for the property.
            min_length (Optional[int]): Minimum length of the text.
            max_length (Optional[int]): Maximum length of the text.
        """
        data = {}
        if min_length is not None:
            data["min_length"] = min_length
        if max_length is not None:
            data["max_length"] = max_length
        self._add_property(key, label, PropertyType.TEXT, data)

    def add_bool(self, key: str, label: str):
        """Adds a boolean property to the collection.
        Args:
            key (str): Unique identifier for the property.
            label (str): Display label for the property.
        """
        self._add_property(key, label, PropertyType.BOOL)
        self.set_default(key, False)

    def add_path(self, key: str, label: str, file_types: Optional[list[str]] = None):
        """Adds a path property to the collection.
        Args:
            key (str): Unique identifier for the property.
            label (str): Display label for the property.
            file_types (Optional[list[str]]): List of allowed file types for the path (e.g., ['.txt', '.jpg']).
        """
        data = {}
        if file_types is not None:
            data["file_types"] = file_types
        self._add_property(key, label, PropertyType.PATH, data)

    def add_select(self, key: str, label: str, options: list[PropertySelectOption]):
        """Adds a select property to the collection.
        Args:
            key (str): Unique identifier for the property.
            label (str): Display label for the property.
            options (list[PropertySelectOption]): List of options for the select property.
        """
        data = {"options": options}
        self._add_property(key, label, PropertyType.SELECT, data)

    def _validate_key(self, key: str):
        """Validates that the property key exists in the collection.
        Args:
            key (str): Unique identifier for the property.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        if key not in self._properties:
            raise ValueError(f"Property with key '{key}' does not exist.")

    def _update_property_data(self, key: str, data: dict[str, Any], property_type: PropertyType):
        """Updates the data of a property.
        Args:
            key (str): Unique identifier for the property.
            data (dict[str, Any]): Data to update in the property.
            property_type (PropertyType): Expected type of the property.
        Raises:
            ValueError: If the property with the given key does not exist or is not of the expected type.
        """
        self._validate_key(key)
        if self._properties[key]._type != property_type:
            raise ValueError(
                f"Property with key '{key}' is not of type '{property_type}'.")

        self._properties[key].data.update(data)

    def update_select_options(self, key: str, options: list[PropertySelectOption]):
        """Updates the options of a select property.
        Args:
            key (str): Unique identifier for the property.
            options (list[PropertySelectOption]): New list of options for the select property.
        Raises:
            ValueError: If the property with the given key does not exist or is not of type 'select'.
        """
        self._update_property_data(
            key, {"options": options}, PropertyType.SELECT)

    def remove_property(self, key: str):
        """Removes a property from the collection.
        Args:
            key (str): Unique identifier for the property to be removed.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        del self._properties[key]

    def get_property(self, key: str) -> Optional[Property]:
        """Retrieves a property by its key.
        Args:
            key (str): Unique identifier for the property.
        Returns:
            Optional[Property]: The property if found, otherwise None.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        return self._properties.get(key, None)

    def has_property(self, key: str) -> bool:
        """Checks if a property exists in the collection.
        Args:
            key (str): Unique identifier for the property.
        Returns:
            bool: True if the property exists, False otherwise.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        return key in self._properties

    def get_type(self, key: str) -> PropertyType:
        """Retrieves the type of a property by its key.
        Args:
            key (str): Unique identifier for the property.
        Returns:
            PropertyType: The type of the property.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        return self._properties[key]._type

    def set_enabled(self, key: str, enabled: bool):
        """Sets the enabled state of a property.
        Args:
            key (str): Unique identifier for the property.
            enabled (bool): True to enable the property, False to disable it.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        self._properties[key].enabled = enabled

    def set_visible(self, key: str, visible: bool):
        """Sets the visibility of a property.
        Args:
            key (str): Unique identifier for the property.
            visible (bool): True to make the property visible, False to hide it.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        self._properties[key].visible = visible

    def set_required(self, key: str, required: bool):
        """Sets the required state of a property.
        Args:
            key (str): Unique identifier for the property.
            required (bool): True to make the property required, False otherwise.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        self._properties[key].required = required

    def set_default(self, key: str, default: Any):
        """Sets the default value for a property.
        Args:
            key (str): Unique identifier for the property.
            default (Any): Default value to set for the property.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        self._properties[key].default = default

    def set_modified_callback(self, key: str, callback: modified_callback_type):
        """Sets a callback function to be called when the settings of property is modified.
        This callback can modify the properties based on the current settings, and if it returns
        a dict[str, Property], those properties will be updated in the Properties instance.
        If the callback returns None, no changes are made to the properties.
        The callback should accept three parameters:
            - `props`: The Properties instance.
            - `settings`: The current Settings instance.
        The callback should return a dictionary of properties to update, or None if no changes are needed.
        Args:
            key (str): Unique identifier for the setting property.
            callback (modified_callback_type): Callback function to set.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        self._properties[key]._modified_callback = callback

    def get_modified_callback(self, key: str) -> Optional[modified_callback_type]:
        """Retrieves the callback function for a setting property.
        Args:
            key (str): Unique identifier for the setting property.
        Returns:
            Optional[modified_callback_type]: The callback function if set, otherwise None.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        return self._properties[key]._modified_callback

    def remove_modified_callback(self, key: str):
        """Removes the callback function for a setting property.
        Args:
            key (str): Unique identifier for the setting property.
        Raises:
            ValueError: If the property with the given key does not exist.
        """
        self._validate_key(key)
        self._properties[key]._modified_callback = None

    def get_default_values(self) -> dict[str, Any]:
        """Returns a dictionary of default values for all properties that have a default set.
        Returns:
            dict[str, Any]: A dictionary where keys are property keys and values are their defaults.
        """
        defaults = {}
        for key, prop in self._properties.items():
            if prop.default is not None:
                defaults[key] = prop.default
        return defaults

    def get_properties(self, settings: Optional[Settings] = None) -> list[Property]:
        """Returns a list of properties, optionally filtered by settings.
        Args:
            settings (Optional[Settings]): Settings to filter properties by. If None, returns all properties.
        Returns:
            list[Property]: A list of properties. If settings are provided, modified properties will be applied.
        """
        if settings is None:
            return list(self._properties.values())
        self_copy = copy.deepcopy(self)
        props = self_copy._properties.copy()
        for key, _ in settings.get_settings().items():
            prop = self_copy.get_property(key)
            if prop and prop._modified_callback:
                # Call the modified callback if it exists, which may modify the properties
                # based on the current settings.
                new_props = prop._modified_callback(self_copy, settings)
                if new_props:
                    props = new_props
                    self_copy._properties.update(new_props)
        return list(props.values())

    def get_properties_dict(self, settings: Optional[Settings] = None) -> list[dict[str, Any]]:
        """Returns a list of properties as dictionaries, optionally filtered by settings.
        Args:
            settings (Optional[Settings]): Settings to filter properties by. If None, returns all properties.
        Returns:
            list[dict[str, Any]]: A list of dictionaries representing the properties.
        """
        props = self.get_properties(settings)
        return [prop.get_dict() for prop in props]

    def validate(self, settings: Settings) -> bool:
        """Validates the properties against the provided settings.
        Args:
            settings (Settings): Settings to validate against.
        Returns:
            bool: True if all properties are valid, otherwise raises an exception.
        Raises:
            ValueError: If any property is invalid according to the settings.
        """
        props = self.get_properties(settings)
        for prop in props:
            self.validate_property(prop, settings)
        return True

    def validate_property(self, prop: Property, settings: Settings):
        """Validates a single property against the provided settings.
        Args:
            prop (Property): The property to validate.
            settings (Settings): Settings to validate against.
        Raises:
            ValueError: If the property is invalid according to the settings.
        """
        key = prop.key
        if prop.required and key not in settings.get_settings():
            raise ValueError(f"Property '{key}' is required.")
        if prop.enabled and key in settings.get_settings():
            value = settings.get_settings()[key]
            validator = VALIDATORS.get(prop._type)
            if not validator:
                raise ValueError(
                    f"Unknown property type '{prop._type}' for key '{key}'.")
            if prop._type == PropertyType.SELECT:
                options = prop.data.get("options", [])
                if not validator(value, options):
                    raise ValueError(
                        f"Property '{key}' must be one of the valid options.")
            elif not validator(value):
                raise ValueError(
                    f"Property '{key}' must be of type '{prop._type.value}'.")
