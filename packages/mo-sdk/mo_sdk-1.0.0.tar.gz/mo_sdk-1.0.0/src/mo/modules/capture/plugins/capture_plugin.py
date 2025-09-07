import typing
from abc import abstractmethod
from typing import Any, Callable

from mo.core.plugin.models.plugin import Plugin

# PicklableScalar is a type that can be serialized with pickle.
PicklableScalar = typing.Union[int, float, str, bool, None, bytes, bytearray]

# PicklableType is a recursive type that can represent any picklable structure,
PicklableType = typing.Union[
    PicklableScalar,
    list["PicklableType"],
    dict[str, "PicklableType"],
    tuple["PicklableType", ...],
    set["PicklableType"],
    frozenset["PicklableType"],
]


class CaptureData:
    """Class representing a single piece of captured data with a timestamp.
    Attributes:
        timestamp (float): The timestamp when the data was captured.
        data (PicklableType): The captured data, which can be any picklable type.
    """

    timestamp: float
    data: PicklableType

    def __init__(self, timestamp: float, data: PicklableType):
        self.timestamp = timestamp
        self.data = data


class CapturePlugin(Plugin):
    """Abstract base class for capture plugins.

    Defines the interface for plugins responsible for capturing data during a session.
    Capture plugins are used to initialize recording, control its execution (pause/resume),
    and persist the captured data periodically.

    Subclasses must implement all abstract methods to define the behavior of a concrete
    data capture source (e.g., video, audio, physiological signals, sensors, etc.).

    Expected lifecycle:
    - `prepare()` is called once to set up the plugin.
    - `start()` initiates the capture process and must actively send data using `on_data`.
      It can be blocking or non-blocking, but must keep the capture running until `stop()` is called.
    - `pause()` and `resume()` allow temporary suspension.
    - `stop()` finalizes the capture session.
    - `save()` is called repeatedly with data batches.
    - `get_file_extension()` specifies the output format.
    - `get_output_descriptor()` can provide additional metadata about the output.

    Notes:
    - Each call to `save()` receives a time-ordered list of `CaptureData` instances. The
      capture system ensures `save()` is invoked regularly, and once more with `end_of_data=True`.
    - This class inherits from `Plugin`, so implementing classes must also define
    `load()` and `unload()` methods for plugin lifecycle management, and may override
    `on_configure()` for handling configuration changes.
    """

    _module_name: str = "capture"

    @abstractmethod
    def prepare(self, path: str, file_name: str) -> None:
        """Prepare the plugin with the given session path and file name.
        Args:
            path (str): The path to the session directory.
            file_name (str): The name of the file where captured data will be saved.
        """
        pass

    @abstractmethod
    def start(
        self,
        start_ts: float,
        get_timestamp: Callable[[], float],
        on_data: Callable[[CaptureData], None],
    ) -> None:
        """Start the capture process.

        This method is called to initiate the data capture process. It may be implemented
        in a blocking or non-blocking way, but must ensure that the plugin remains active
        and continuously captures data while the session is running.

        Captured data must be sent through the `on_data` callback as instances of
        `CaptureData`, including the appropriate timestamp and data. The plugin is
        responsible for invoking this callback for every piece of data it captures
        until `stop()` is called.
        Args:
            start_ts (float): The timestamp when the capture starts.
            get_timestamp (Callable[[], float]): A callable that returns the current timestamp.
            on_data (Callable[[CaptureData], None]): A callback function to handle captured data.
        """
        pass

    @abstractmethod
    def pause(self, pause_ts: float) -> None:
        """Pause the capture process.

        This method is called to pause the capture process, allowing the plugin to
        temporarily stop capturing data.
        Args:
            pause_ts (float): The timestamp when the capture is paused.
        """
        pass

    @abstractmethod
    def resume(self, resume_ts: float) -> None:
        """Resume the capture process after it has been paused.

        This method is called to resume capturing data after a pause.
        Args:
            resume_ts (float): The timestamp when the capture is resumed.
        """
        pass

    @abstractmethod
    def stop(self, stop_ts: float) -> None:
        """Stop the capture process.

        This method is called to stop the capture process, allowing the plugin to
        finalize any captured data and prepare for saving the last data.
        Args:
            stop_ts (float): The timestamp when the capture is stopped.
        """
        pass

    @abstractmethod
    def save(self, data: list[CaptureData], end_of_data: bool = False) -> None:
        """Save the captured data.

        This method persists a batch of data captured by the plugin, received via the
        `on_data` callback during execution of the `start` method.
        The data is a list of `CaptureData` instances, ordered chronologically within
        a time window that may be fixed or dynamic.
        It is called periodically to store data incrementally. If `end_of_data` is True,
        this is the final batch.
        Args:
            data (list[CaptureData]): A list of `CaptureData` instances to be saved.
            end_of_data (bool): Indicates whether this is the final set of captured data.
                Defaults to False.
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension used by the plugin for saving captured data.
        Returns:
            str: The file extension used by the plugin, or an empty string if not applicable.
        """
        pass
    
    def get_output_descriptor(self) -> dict[str, Any] | None:
        """Get the output descriptor for the plugin.

        This method can be overridden to provide additional metadata about the output
        of the plugin, such as format, encoding, or other relevant information.
        Returns:
            dict[str, Any] | None: A dictionary containing output metadata, or None if not applicable.
        """
        return None
