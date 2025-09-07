from typing import Callable, Any
from mo.modules.capture import CapturePlugin, CaptureData
from mo.core import load_metadata_json


@load_metadata_json("../..")
class ClassName(CapturePlugin):
    """
    Base implementation for a capture plugin.

    This class is intended to be a starting point for a capture plugin that inherits from
    CapturePlugin. It provides the required structure and documentation for all methods
    that need to be implemented to comply with the plugin system.

    Expected lifecycle:
    - `prepare()` is called once to set up the plugin.
    - `start()` initiates the capture process and must actively send data using `on_data`.
      It can be blocking or non-blocking, but must keep the capture running until `stop()` is called.
    - `pause()` and `resume()` allow temporary suspension.
    - `stop()` finalizes the capture session.
    - `save()` is called repeatedly with data batches.
    - `get_file_extension()` specifies the output format.

    Notes:
    - Each call to `save()` receives a time-ordered list of `CaptureData` instances. The
      capture system ensures `save()` is invoked regularly, and once more with `end_of_data=True`.
    - This class inherits from `CapturePlugin`, so implementing classes must define
      all abstract methods and may override `on_configure()` for handling configuration changes.
    """

    def load(self):
        """
        Load and initialize the plugin.

        This method should perform any required setup to make the plugin operational.
        It is called once when the plugin is loaded by the system.

        Typical tasks include: resource allocation, starting background tasks,
        establishing connections, or validating initial state.
        """
        pass

    def unload(self):
        """
        Unload and clean up the plugin.

        This method should release any resources acquired during `load()`, stop ongoing
        tasks, and leave the system in a clean state. It is called when the plugin is
        removed.
        """
        pass

    def prepare(self, path: str, file_name: str):
        """
        Prepare the plugin with the given session path and file name.

        Args:
            path (str): The path to the session directory.
            file_name (str): The name of the file where captured data will be saved.
        """
        pass

    def start(self, start_ts: float, get_timestamp: Callable[[], float], on_data: Callable[[CaptureData], None]):
        """
        Start the capture process.

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

    def pause(self, pause_ts: float):
        """
        Pause the capture process.

        This method is called to pause the capture process, allowing the plugin to
        temporarily stop capturing data.

        Args:
            pause_ts (float): The timestamp when the capture is paused.
        """
        pass

    def resume(self, resume_ts: float):
        """
        Resume the capture process after it has been paused.

        This method is called to resume capturing data after a pause.

        Args:
            resume_ts (float): The timestamp when the capture is resumed.
        """
        pass

    def stop(self, stop_ts: float):
        """
        Stop the capture process.

        This method is called to stop the capture process, allowing the plugin to
        finalize any captured data and prepare for saving the last data.

        Args:
            stop_ts (float): The timestamp when the capture is stopped.
        """
        pass

    def save(self, data: list[CaptureData], end_of_data: bool = False):
        """
        Save the captured data.

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

    def get_file_extension(self) -> str:
        """
        Get the file extension used by the plugin for saving captured data.

        Returns:
            str: The file extension used by the plugin, or an empty string if not applicable.
        """
        return ""

    def get_output_descriptor(self) -> dict[str, Any] | None:
        """Get the output descriptor for the plugin.

        This method can be overridden to provide additional metadata about the output
        of the plugin, such as format, encoding, or other relevant information.
        Returns:
            dict[str, Any] | None: A dictionary containing output metadata, or None if not applicable.
        """
        return None
